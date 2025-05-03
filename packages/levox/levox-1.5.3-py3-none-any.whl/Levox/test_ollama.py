import ollama
import sys

def test_ollama_connection():
    """Test basic Ollama connection and APIs"""
    print("Testing Ollama connection...")
    try:
        # Test the list models API
        print("\nTesting ollama.list():")
        models = ollama.list()
        print(f"Models response type: {type(models)}")
        
        # Handle ListResponse (newer Ollama versions return a custom object)
        if hasattr(models, 'models'):
            print("Found 'models' attribute in response")
            models_list = models.models
            print(f"Models list: {models_list}")
            
            # Check if our model exists in the list of models
            model_name = "deepseek-r1:1.5b"
            model_exists = False
            for model in models_list:
                if hasattr(model, 'model') and model.model == model_name:
                    model_exists = True
                    print(f"Found model: {model.model}")
                    break
            
            print(f"Model {model_name} exists: {model_exists}")
            
            # Test basic generation with the model
            if model_exists:
                print("\nTesting basic generation:")
                try:
                    # Try different parameter combinations
                    try:
                        print("Trying with older parameter style...")
                        response = ollama.generate(
                            model=model_name,
                            prompt="What is GDPR?",
                        )
                    except TypeError:
                        print("Trying with newer parameter style...")
                        response = ollama.chat(
                            model=model_name,
                            messages=[{"role": "user", "content": "What is GDPR?"}]
                        )
                    
                    print(f"Generation response type: {type(response)}")
                    
                    if hasattr(response, 'response'):
                        print(f"Generated text: {response.response[:100]}...")
                    elif hasattr(response, 'message') and hasattr(response.message, 'content'):
                        print(f"Generated text: {response.message.content[:100]}...")
                    elif isinstance(response, dict):
                        if 'response' in response:
                            print(f"Generated text: {response['response'][:100]}...")
                        elif 'message' in response and 'content' in response['message']:
                            print(f"Generated text: {response['message']['content'][:100]}...")
                    else:
                        print(f"Unexpected response format: {type(response)}")
                        print(f"Available attributes: {dir(response)}")
                except Exception as e:
                    print(f"Error during generation: {e}")
                    print(f"Error type: {type(e)}")
                    import traceback
                    traceback.print_exc()
        else:
            print("Could not find models in the response")
        
        return True
    except Exception as e:
        print(f"Error testing Ollama: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ollama_connection() 