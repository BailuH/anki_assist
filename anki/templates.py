import time
import genanki


def basic_model() -> genanki.Model:
    return genanki.Model(
        model_id=1607392319,
        name="Legal-Basic-Model",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
            {"name": "SourceDoc"},
            {"name": "SourceLoc"},
            {"name": "Tags"},
            {"name": "Difficulty"},
            {"name": "Evidence"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": (
                    "<div class='wrap'>"
                    "  <div class='header'>法律学习卡片</div>"
                    "  <div class='question'>{{Question}}</div>"
                    "</div>"
                ),
                "afmt": (
                    "{{FrontSide}}"
                    "<hr class='sep'>"
                    "<div class='wrap'>"
                    "  <div class='answer card-block'>{{Answer}}</div>"
                    "  <div class='meta-grid'>"
                    "    <div class='meta-item'><span class='label'>来源文档</span><span class='value'>{{SourceDoc}}</span></div>"
                    "    <div class='meta-item'><span class='label'>定位</span><span class='value'>{{SourceLoc}}</span></div>"
                    "    <div class='meta-item'><span class='label'>难度</span><span class='value'>{{Difficulty}}</span></div>"
                    "    <div class='meta-item'><span class='label'>标签</span><span class='value tags'>{{Tags}}</span></div>"
                    "  </div>"
                    "  <details class='evidence'><summary>证据片段</summary><div class='evidence-body'>{{Evidence}}</div></details>"
                    "</div>"
                ),
            }
        ],
        css="""
:root{--bg:#ffffff;--fg:#1f2328;--muted:#6e7781;--primary:#1f6feb;--border:#eaeef2;--card:#f6f8fa;--tag:#eef2ff;--tag-border:#c7d2fe;--tag-fg:#3730a3;--easy:#dcfce7;--easy-b:#86efac;--easy-f:#166534;--med:#fef9c3;--med-b:#fde047;--med-f:#854d0e;--hard:#fee2e2;--hard-b:#fca5a5;--hard-f:#7f1d1d}
@media (prefers-color-scheme: dark){:root{--bg:#0d1117;--fg:#e6edf3;--muted:#9ea7b3;--primary:#79c0ff;--border:#30363d;--card:#151b23;--tag:#1e293b;--tag-border:#334155;--tag-fg:#cbd5e1;--easy:#052e16;--easy-b:#14532d;--easy-f:#86efac;--med:#3f2d04;--med-b:#713f12;--med-f:#fde68a;--hard:#3f1d1d;--hard-b:#7f1d1d;--hard-f:#fecaca}} 
.card{background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Noto Sans SC',sans-serif;line-height:1.6;font-size:16px;}
.wrap{max-width:760px;margin:0 auto;padding:8px 2px;}
.header{font-size:12px;color:var(--muted);letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px;}
.question{font-size:22px;font-weight:700;margin:8px 0 2px;}
.sep{border:none;border-top:1px solid var(--border);margin:10px 0;}
.card-block{background:linear-gradient(180deg,rgba(31,111,235,.07),rgba(31,111,235,.03));border:1px solid var(--border);border-radius:10px;padding:14px 16px;box-shadow:0 2px 10px rgba(0,0,0,.04);margin:8px 0 14px;white-space:pre-wrap;}
.meta-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:8px 0 6px;}
@media (max-width:520px){.meta-grid{grid-template-columns:1fr;}}
.meta-item{display:flex;gap:8px;align-items:baseline;border-left:3px solid var(--border);padding-left:8px;}
.label{color:var(--muted);font-size:12px;min-width:64px;}
.value{font-size:14px;}
.tags .tag{display:inline-block;background:var(--tag);border:1px solid var(--tag-border);color:var(--tag-fg);border-radius:999px;padding:2px 8px;margin-right:6px;margin-bottom:4px;font-size:12px;}
.badge{display:inline-block;border-radius:6px;padding:2px 8px;font-size:12px;border:1px solid var(--border)}
.diff-easy{background:var(--easy);border-color:var(--easy-b);color:var(--easy-f)}
.diff-medium{background:var(--med);border-color:var(--med-b);color:var(--med-f)}
.diff-hard{background:var(--hard);border-color:var(--hard-b);color:var(--hard-f)}
.diff-unknown{background:var(--card);color:var(--muted)}
.evidence{margin-top:8px;}
.evidence summary{cursor:pointer;color:var(--primary);}
.evidence-body{margin-top:6px;background:var(--card);border:1px dashed var(--border);border-radius:8px;padding:10px;white-space:pre-wrap;}
""",
    )


def cloze_model() -> genanki.Model:
    return genanki.Model(
        model_id=998877665,
        name="Legal-Cloze-Model",
        fields=[
            {"name": "Text"},
            {"name": "SourceDoc"},
            {"name": "SourceLoc"},
            {"name": "Tags"},
            {"name": "Difficulty"},
            {"name": "Evidence"},
        ],
        templates=[
            {
                "name": "Cloze",
                "qfmt": (
                    "<div class='wrap'>"
                    "  <div class='header'>法律学习卡片 · Cloze</div>"
                    "  <div class='cloze'>{{cloze:Text}}</div>"
                    "</div>"
                ),
                "afmt": (
                    "{{FrontSide}}<hr class='sep'>"
                    "<div class='wrap'>"
                    "  <div class='meta-grid'>"
                    "    <div class='meta-item'><span class='label'>来源文档</span><span class='value'>{{SourceDoc}}</span></div>"
                    "    <div class='meta-item'><span class='label'>定位</span><span class='value'>{{SourceLoc}}</span></div>"
                    "    <div class='meta-item'><span class='label'>难度</span><span class='value'>{{Difficulty}}</span></div>"
                    "    <div class='meta-item'><span class='label'>标签</span><span class='value tags'>{{Tags}}</span></div>"
                    "  </div>"
                    "  <details class='evidence'><summary>证据片段</summary><div class='evidence-body'>{{Evidence}}</div></details>"
                    "</div>"
                ),
            }
        ],
        css="""
:root{--bg:#ffffff;--fg:#1f2328;--muted:#6e7781;--primary:#1f6feb;--border:#eaeef2;--card:#f6f8fa;--tag:#eef2ff;--tag-border:#c7d2fe;--tag-fg:#3730a3;--easy:#dcfce7;--easy-b:#86efac;--easy-f:#166534;--med:#fef9c3;--med-b:#fde047;--med-f:#854d0e;--hard:#fee2e2;--hard-b:#fca5a5;--hard-f:#7f1d1d}
@media (prefers-color-scheme: dark){:root{--bg:#0d1117;--fg:#e6edf3;--muted:#9ea7b3;--primary:#79c0ff;--border:#30363d;--card:#151b23;--tag:#1e293b;--tag-border:#334155;--tag-fg:#cbd5e1;--easy:#052e16;--easy-b:#14532d;--easy-f:#86efac;--med:#3f2d04;--med-b:#713f12;--med-f:#fde68a;--hard:#3f1d1d;--hard-b:#7f1d1d;--hard-f:#fecaca}} 
.card{background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Noto Sans SC',sans-serif;line-height:1.6;font-size:16px;}
.wrap{max-width:760px;margin:0 auto;padding:8px 2px;}
.header{font-size:12px;color:var(--muted);letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px;}
.cloze{font-size:20px;font-weight:600;}
.cloze .cloze{color:var(--primary);}
.sep{border:none;border-top:1px solid var(--border);margin:10px 0;}
.meta-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:8px 0 6px;}
@media (max-width:520px){.meta-grid{grid-template-columns:1fr;}}
.meta-item{display:flex;gap:8px;align-items:baseline;border-left:3px solid var(--border);padding-left:8px;}
.label{color:var(--muted);font-size:12px;min-width:64px;}
.value{font-size:14px;}
.tags .tag{display:inline-block;background:var(--tag);border:1px solid var(--tag-border);color:var(--tag-fg);border-radius:999px;padding:2px 8px;margin-right:6px;margin-bottom:4px;font-size:12px;}
.badge{display:inline-block;border-radius:6px;padding:2px 8px;font-size:12px;border:1px solid var(--border)}
.diff-easy{background:var(--easy);border-color:var(--easy-b);color:var(--easy-f)}
.diff-medium{background:var(--med);border-color:var(--med-b);color:var(--med-f)}
.diff-hard{background:var(--hard);border-color:var(--hard-b);color:var(--hard-f)}
.diff-unknown{background:var(--card);color:var(--muted)}
.evidence{margin-top:8px;}
.evidence summary{cursor:pointer;color:var(--primary);}
.evidence-body{margin-top:6px;background:var(--card);border:1px dashed var(--border);border-radius:8px;padding:10px;white-space:pre-wrap;}
""",
        model_type=genanki.Model.CLOZE,
    )
