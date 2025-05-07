"""
Entry point for the Factorio Learning Environment CLI.
"""

def main():
    """Main entry point for the CLI."""
    print("Factorio Learning Environment v0.2.0")
    
    try:
        from .agents import agent_abc
        print("Full package installation available. Type 'factorio-env --help' for usage information.")
    except ImportError:
        print("This appears to be a minimal installation.")
        print("Please refer to the documentation for full functionality.")

if __name__ == "__main__":
    main()
