# -*- coding: utf-8 -*-
"""
Fine-tune a local open-source image matcher from corrected project groups.

Example:
python school_project/train_ai_matcher.py --project web_runtime/projects/<id>.json --epochs 8
"""

import argparse
import json
import random
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="Project JSON exported by the web app")
    parser.add_argument("--output", default="models/ai_matcher.pt")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--projection-dim", type=int, default=512)
    parser.add_argument("--freeze-backbone", action="store_true")
    return parser.parse_args()


def load_samples(project_path):
    with open(project_path, "r", encoding="utf-8") as project_file:
        state = json.load(project_file)
    groups = state.get("results") or state.get("groups") or []
    samples = []
    for label, group in enumerate(groups):
        for image in group.get("images", []):
            path = Path(image.get("source_path", ""))
            if path.exists():
                samples.append((str(path), label))
    if len({label for _, label in samples}) < 2:
        raise ValueError("Training needs at least two corrected groups.")
    return samples


def supervised_contrastive_loss(features, labels, temperature=0.08):
    import torch
    import torch.nn.functional as functional

    features = functional.normalize(features, dim=1)
    logits = features @ features.T / temperature
    labels = labels.view(-1, 1)
    mask = torch.eq(labels, labels.T).float()
    logits_mask = torch.ones_like(mask) - torch.eye(mask.shape[0], device=mask.device)
    mask = mask * logits_mask
    exp_logits = torch.exp(logits) * logits_mask
    log_prob = logits - torch.log(exp_logits.sum(1, keepdim=True).clamp_min(1e-8))
    positives = mask.sum(1).clamp_min(1.0)
    mean_log_prob_pos = (mask * log_prob).sum(1) / positives
    return -mean_log_prob_pos.mean()


def main():
    args = parse_args()
    import torch
    import torchvision.models as models
    import torchvision.transforms as transforms
    from PIL import Image
    from torch.utils.data import DataLoader, Dataset

    class ImageGroupDataset(Dataset):
        def __init__(self, samples):
            self.samples = samples
            self.transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.RandomResizedCrop(224, scale=(0.72, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(0.16, 0.16, 0.12, 0.04),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, index):
            path, label = self.samples[index]
            image = Image.open(path).convert("RGB")
            return self.transform(image), int(label)

    samples = load_samples(args.project)
    random.shuffle(samples)
    dataset = ImageGroupDataset(samples)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, drop_last=len(dataset) > args.batch_size)

    weights = models.ResNet50_Weights.DEFAULT
    model = models.resnet50(weights=weights)
    if args.freeze_backbone:
        for parameter in model.parameters():
            parameter.requires_grad = False
    in_features = model.fc.in_features
    model.fc = torch.nn.Linear(in_features, args.projection_dim)
    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=args.lr, weight_decay=1e-4)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.train()
    for epoch in range(args.epochs):
        total = 0.0
        steps = 0
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            features = model(images)
            loss = supervised_contrastive_loss(features, labels)
            loss.backward()
            optimizer.step()
            total += float(loss.detach().cpu())
            steps += 1
        print("epoch", epoch + 1, "loss", round(total / max(1, steps), 4))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "arch": "resnet50",
        "projection_dim": args.projection_dim,
        "model": model.cpu().state_dict(),
    }, output)
    print("saved", output)


if __name__ == "__main__":
    main()
