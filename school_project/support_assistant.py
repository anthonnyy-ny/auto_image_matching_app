# -*- coding: utf-8 -*-


SYSTEM_HELP = {
    "create": "先在 Dashboard 的输入框写项目名称，然后点 Create。建立项目后，再上传图片或 ZIP。",
    "upload": "建立项目后，在输入区选择图片或 ZIP。系统会分批上传，状态条会显示上传进度。",
    "match": "上传完成后，选择 AI Hybrid、AI Vector 或 Trained AI，然后点 Run。新手建议先用 AI Hybrid。",
    "results": "匹配完成后，Matched Sets 会显示分组结果。点击图片可选择，双击可预览大图。",
    "edit": "如果分错了，可以选择图片后点 New Set、Remove，或选择多个组点 Merge。改完记得点 Save。",
    "export": "Current project 卡片里有 Project JSON 和 Export ZIP。Export ZIP 会按分组打包图片。",
    "ai": "AI solution 卡片会显示当前模型状态。Fallback 表示没有加载 Hugging Face 或本地训练模型，但系统仍可用。",
    "model": "要启用 Hugging Face 模型，需要设置 AI_ALLOW_DOWNLOAD=1，并启动后端。默认模型是 facebook/dinov2-base。",
    "train": "先人工修正分组并保存项目 JSON，再用 train_ai_matcher.py 训练，输出 models/ai_matcher.pt。",
    "cache": "如果图片或模型状态怪怪的，可以点 Clear cache。它会清掉传统特征和 AI embedding 缓存。",
}


def assistant_reply(message, context=None):
    text = (message or "").strip()
    lowered = text.lower()
    if not text:
        return _wrap("你可以直接问我：怎么上传图片、怎么运行 AI、怎么导出结果，或为什么 AI 显示 Fallback。")

    if _has_any(lowered, ["创建", "create", "new project", "项目"]):
        return _wrap(SYSTEM_HELP["create"])
    if _has_any(lowered, ["上传", "upload", "zip", "图片", "照片"]):
        return _wrap(SYSTEM_HELP["upload"])
    if _has_any(lowered, ["运行", "匹配", "match", "run", "ai hybrid", "ai vector"]):
        return _wrap(SYSTEM_HELP["match"])
    if _has_any(lowered, ["结果", "分组", "results", "sets", "matched"]):
        return _wrap(SYSTEM_HELP["results"])
    if _has_any(lowered, ["修改", "修正", "合并", "删除", "edit", "merge", "remove", "save"]):
        return _wrap(SYSTEM_HELP["edit"])
    if _has_any(lowered, ["导出", "export", "json", "zip"]):
        return _wrap(SYSTEM_HELP["export"])
    if _has_any(lowered, ["fallback", "huggingface", "hugging face", "模型", "model", "dinov2"]):
        return _wrap(SYSTEM_HELP["ai"] + " " + SYSTEM_HELP["model"])
    if _has_any(lowered, ["训练", "train", "微调", "fine tune", "finetune"]):
        return _wrap(SYSTEM_HELP["train"])
    if _has_any(lowered, ["缓存", "cache", "清除", "clear"]):
        return _wrap(SYSTEM_HELP["cache"])
    if _has_any(lowered, ["错误", "error", "失败", "failed", "不能", "打不开"]):
        return _wrap("先看 Run State 的错误文字。如果是模型相关，多半是 Hugging Face 权重还没下载；如果是上传相关，确认文件是图片或 ZIP；如果匹配没结果，先用 AI Hybrid 再试一次。")

    return _wrap(
        "我可以帮你一步步操作这个网站。新手最稳流程是：Create 建项目 -> 上传图片/ZIP -> 选择 AI Hybrid -> Run -> 检查 Matched Sets -> Save -> Export ZIP。"
    )


def _has_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def _wrap(answer):
    return {
        "role": "assistant",
        "name": "Guardian Goddess",
        "answer": answer,
        "suggestions": [
            "怎么上传图片？",
            "为什么 AI 是 Fallback？",
            "怎么导出分组结果？",
        ],
    }
