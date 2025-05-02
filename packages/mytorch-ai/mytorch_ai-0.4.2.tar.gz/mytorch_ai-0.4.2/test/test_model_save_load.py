
def test_save_load_model():
    import torch
    import hashlib
    import os

    # Create simple tensor state_dict
    a = torch.randn(3, 3)
    b = torch.ones(2, 2)

    state_dict = {
        "layer1.weight": a,
        "layer2.bias": b,
    }

    # Save using PyTorch
    torch.save( state_dict, "saved_model.pt" )

    # Load and verify, 
    loaded = torch.load("saved_model.pt")
    assert "layer1.weight" in loaded
    assert "layer2.bias" in loaded
    assert torch.equal(loaded["layer1.weight"], a)
    assert torch.equal(loaded["layer2.bias"], b)

    print("Simple model save test passed.")

def test_resnet18_save_load():
    import torch
    import torchvision.models as models
    import os

    # Load pretrained ResNet-18 and switch to eval mode
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.eval()

    # Extract and save the state_dict
    original_state_dict = model.state_dict()
    torch.save(original_state_dict, "resnet18_saved.pt")

    # Load state_dict into a fresh instance
    model_loaded = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model_loaded.load_state_dict(torch.load("resnet18_saved.pt"))
    model_loaded.eval()

    # Efficient comparison via state_dict keys
    loaded_sd = model_loaded.state_dict()

    assert original_state_dict.keys() == loaded_sd.keys(), "Mismatch in state_dict keys"

    for key in original_state_dict:
        v1 = original_state_dict[key]
        v2 = loaded_sd[key]
        assert torch.equal(v1, v2), f"Mismatch in parameter: {key}"

    print("✅ ResNet-18 save/load test passed.")


def main():
    test_save_load_model()
    test_resnet18_save_load()

if __name__ == "__main__":
    main()
