import crewai
print(f"CrewAI version: {crewai.__version__}")

# Check embedder config
try:
    from crewai.knowledge.embedder.openai_embedder import OpenAIEmbedder
    import inspect
    sig = inspect.signature(OpenAIEmbedder.__init__)
    print(f"\nOpenAIEmbedder.__init__ parameters: {sig}")
except Exception as e:
    print(f"Error: {e}")

# Try alternative path
try:
    from crewai.utilities import Embedder
    import inspect
    sig = inspect.signature(Embedder.__init__)
    print(f"\nEmbedder.__init__ parameters: {sig}")
except Exception as e:
    print(f"Error 2: {e}")