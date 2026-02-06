from datagent.db.fs import db
from datagent.db.repositories.session import SessionRepository
from datagent.core.context import WorkflowContext

def test_storage():
    print("Testing FileSystemDB and SessionRepository...")
    
    repo = SessionRepository()
    
    # Create a dummy context
    ctx = WorkflowContext(session_id="test-db-session")
    ctx = ctx.update({"foo": "bar"})
    ctx = ctx.add_history("User said hello")
    
    # Save
    print(f"Saving session {ctx.session_id}...")
    repo.save(ctx)
    
    # Verify file exists
    import os
    expected_path = os.path.join(db.root_dir, "sessions", "test-db-session.json")
    if os.path.exists(expected_path):
        print(f"SUCCESS: File created at {expected_path}")
    else:
        print(f"FAILURE: File not found at {expected_path}")
        
    # Load
    print("Loading session...")
    loaded_ctx = repo.load("test-db-session")
    print(f"Loaded State: {loaded_ctx.state}")
    print(f"Loaded History: {loaded_ctx.history}")
    
    assert loaded_ctx.state["foo"] == "bar"
    assert loaded_ctx.history[0] == "User said hello"
    
    print("Test Complete.")

if __name__ == "__main__":
    test_storage()
