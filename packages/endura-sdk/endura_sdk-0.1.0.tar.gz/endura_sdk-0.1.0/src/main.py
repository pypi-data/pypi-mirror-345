from agent import EnduraAgent

def main():
    model_path = "model.pth"

    agent = EnduraAgent(model_path)

    print(f"Model Metadata: {agent.model_meta}")

if __name__ == "__main__":
    main()