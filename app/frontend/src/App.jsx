import { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Paperclip, Bot, User, Cpu, X, File as FileIcon, Loader } from 'lucide-react';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [files, setFiles] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const uploadFile = async (file) => {
    // Create a new file object with upload status
    const newFile = {
      file: file,
      name: file.name,
      progress: 0,
      status: 'uploading', // uploading, done, error
      url: null
    };

    setFiles(prev => [...prev, newFile]);

    const formData = new FormData();
    formData.append('file', file);

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', 'http://localhost:8000/api/v1/workflow/upload', true);

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          setFiles(prev => prev.map(f => 
            f.file === file ? { ...f, progress: percentComplete } : f
          ));
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          setFiles(prev => prev.map(f => 
            f.file === file ? { ...f, status: 'done', url: response.url, progress: 100 } : f
          ));
          resolve(response);
        } else {
          setFiles(prev => prev.map(f => 
            f.file === file ? { ...f, status: 'error', progress: 0 } : f
          ));
          reject(new Error('Upload failed'));
        }
      };

      xhr.onerror = () => {
        setFiles(prev => prev.map(f => 
          f.file === file ? { ...f, status: 'error', progress: 0 } : f
        ));
        reject(new Error('Upload failed'));
      };

      xhr.send(formData);
    });
  };

  const handleFileSelect = async (selectedFiles) => {
    const fileArray = Array.from(selectedFiles);
    // Trigger uploads for all files
    await Promise.all(fileArray.map(uploadFile));
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      handleFileSelect(e.target.files);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files) {
      await handleFileSelect(e.dataTransfer.files);
    }
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Check if any files are still uploading
    const isUploading = files.some(f => f.status === 'uploading');
    if (isUploading) return;

    if ((!input.trim() && files.length === 0) || isStreaming) return;

    // Filter only successfully uploaded files
    const uploadedFiles = files.filter(f => f.status === 'done');

    const userMessage = {
      role: 'user',
      content: input,
      files: uploadedFiles.map(f => f.name),
      id: Date.now().toString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    const formData = new FormData();
    formData.append('prompt', input);
    if (sessionId) {
      formData.append('session_id', sessionId);
    }
    
    // Send file metadata as JSON
    if (uploadedFiles.length > 0) {
      const filesMetadata = uploadedFiles.map(f => ({
        filename: f.name,
        url: f.url,
        timestamp: new Date().toISOString() // Assuming current time or returned from server
      }));
      formData.append('files', JSON.stringify(filesMetadata));
    }
    
    setFiles([]);

    try {
      const response = await fetch('http://localhost:8000/api/v1/workflow/stream', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      // Create a placeholder for the assistant response
      const assistantMsgId = Date.now().toString() + '-ai';
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '',
        id: assistantMsgId,
        isThinking: true,
        thoughts: []
      }]);

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (dataStr === '[DONE]') {
              setIsStreaming(false);
              break;
            }

            try {
              const event = JSON.parse(dataStr);
              
              setMessages(prev => {
                const newMessages = [...prev];
                const currentMsg = newMessages.find(m => m.id === assistantMsgId);
                if (!currentMsg) return prev;

                if (event.type === 'text_chunk') {
                  currentMsg.content += event.content || '';
                  currentMsg.isThinking = false;
                } else if (event.type === 'node_start') {
                  currentMsg.thoughts.push(`Starting: ${event.data.agent || 'Unknown Agent'}`);
                } else if (event.type === 'router_decision') {
                  currentMsg.thoughts.push(`Routing: ${event.data.condition} -> ${event.data.next_node}`);
                } else if (event.type === 'tool_start') {
                  currentMsg.thoughts.push(`Tool: ${event.data.tool_name}`);
                } else if (event.type === 'error') {
                  currentMsg.content += `\n\n*Error: ${event.content}*`;
                }
                
                return newMessages;
              });

            } catch (e) {
              console.error('Error parsing SSE:', e);
            }
          }
        }
      }

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, an error occurred while connecting to the server.',
        id: Date.now().toString(),
        error: true
      }]);
    } finally {
      setIsStreaming(false);
    }
  };

  const isSubmitDisabled = (!input.trim() && files.length === 0) || isStreaming || files.some(f => f.status === 'uploading');

  return (
    <div 
      className={`app-container ${isDragging ? 'dragging' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <header className="app-header">
        <h1>Avaloka AI</h1>
      </header>
      
      <main className="chat-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <Bot size={48} />
            <h2>How can I help you today?</h2>
          </div>
        )}
        
        <div className="messages-list">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.role}`}>
              <div className="avatar">
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>
              <div className="message-content">
                <div className="sender-name">{msg.role === 'user' ? 'You' : 'Avaloka Agent'}</div>
                
                {msg.role === 'user' && msg.files && msg.files.length > 0 && (
                  <div className="file-attachments">
                    {msg.files.map((f, i) => (
                      <div key={i} className="file-chip">
                        <FileIcon size={14} /> {f}
                      </div>
                    ))}
                  </div>
                )}

                {msg.thoughts && msg.thoughts.length > 0 && (
                  <div className="thoughts">
                    <div className="thoughts-header"><Cpu size={14} /> Processing...</div>
                    {msg.thoughts.map((thought, i) => (
                      <div key={i} className="thought-item">{thought}</div>
                    ))}
                  </div>
                )}
                
                <div className="markdown-body">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
          {isStreaming && messages.length > 0 && messages[messages.length - 1].role === 'user' && (
             <div className="message assistant">
               <div className="avatar"><Bot size={20} /></div>
               <div className="message-content">
                 <div className="typing-indicator">Thinking...</div>
               </div>
             </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="input-area">
        {isDragging && (
           <div className="drag-overlay">
             <div className="drag-content">
               <FileIcon size={48} />
               <h3>Drop files here to upload</h3>
             </div>
           </div>
        )}
        
        <div className="input-container">
          {files.length > 0 && (
            <div className="file-previews">
              {files.map((file, i) => (
                <div key={i} className={`file-preview-chip ${file.status}`}>
                  <FileIcon size={14} />
                  <div className="file-info">
                    <span className="file-name">{file.name}</span>
                    {file.status === 'uploading' && (
                      <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${file.progress}%` }}></div>
                      </div>
                    )}
                  </div>
                  {file.status === 'uploading' ? (
                     <Loader size={12} className="spinner" />
                  ) : (
                    <button onClick={() => removeFile(i)}><X size={12} /></button>
                  )}
                </div>
              ))}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="input-form">
            <button 
              type="button" 
              className="attach-btn"
              onClick={() => fileInputRef.current?.click()}
            >
              <Paperclip size={20} />
            </button>
            <input 
              type="file" 
              multiple 
              ref={fileInputRef} 
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
            
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Message Avaloka AI..."
              rows={1}
            />
            
            <button 
              type="submit" 
              className="send-btn"
              disabled={isSubmitDisabled}
            >
              <Send size={20} />
            </button>
          </form>
        </div>
        <div className="disclaimer">
          AI can make mistakes. Please verify important information.
        </div>
      </footer>
    </div>
  );
}

export default App;
