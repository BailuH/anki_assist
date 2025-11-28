import time
import genanki


def basic_model() -> genanki.Model:
    return genanki.Model(
        model_id=1607392319,
        name="Legal-Review-Basic",
        fields=[
            {"name": "Question"},
            {"name": "Answer"}, 
            {"name": "SourceDoc"},
            {"name": "SourceLoc"},
            {"name": "Tags"},
            {"name": "Difficulty"},
            {"name": "Evidence"},
            {"name": "CardType"},  # 新增：卡片类型标识
        ],
        templates=[
            {
                "name": "知识问答卡",
                "qfmt": (
                    "<div class='wrap'>"
                    "  <div class='header'>📚 法律复习卡片</div>"
                    "  <div class='card-type'>知识问答</div>"
                    "  <div class='question'>{{Question}}</div>"
                    "</div>"
                ),
                "afmt": (
                    "{{FrontSide}}"
                    "<hr class='sep'>"
                    "<div class='wrap'>"
                    "  <div class='answer card-block'>{{Answer}}</div>"
                    "  <div class='meta-grid'>"
                    "    <div class='meta-item'><span class='label'>📄 来源</span><span class='value'>{{SourceDoc}}</span></div>"
                    "    <div class='meta-item'><span class='label'>📍 位置</span><span class='value'>{{SourceLoc}}</span></div>"
                    "    <div class='meta-item'><span class='label'>⭐ 难度</span><span class='value'>{{Difficulty}}</span></div>"
                    "    <div class='meta-item'><span class='label'>🏷️ 标签</span><span class='value tags'>{{Tags}}</span></div>"
                    "  </div>"
                    "  <details class='evidence'><summary>📋 证据片段</summary><div class='evidence-body'>{{Evidence}}</div></details>"
                    "</div>"
                ),
            },
            {
                "name": "背诵记忆卡",
                "qfmt": (
                    "<div class='wrap'>"
                    "  <div class='header'>🎯 法律背诵卡片</div>"
                    "  <div class='card-type memory'>背诵记忆</div>"
                    "  <div class='memory-hint'>{{Question}}</div>"
                    "  <div class='memory-tip'>💡 点击显示答案进行背诵</div>"
                    "</div>"
                ),
                "afmt": (
                    "{{FrontSide}}"
                    "<hr class='sep'>"
                    "<div class='wrap'>"
                    "  <div class='memory-answer card-block'>{{Answer}}</div>"
                    "  <div class='memory-actions'>"
                    "    <button class='memory-btn easy' onclick='pycmd(\"ease1\");'>😊 记得</button>"
                    "    <button class='memory-btn hard' onclick='pycmd(\"ease3\");'>😰 忘了</button>"
                    "  </div>"
                    "  <div class='meta-grid'>"
                    "    <div class='meta-item'><span class='label'>📄 来源</span><span class='value'>{{SourceDoc}}</span></div>"
                    "    <div class='meta-item'><span class='label'>📍 位置</span><span class='value'>{{SourceLoc}}</span></div>"
                    "  </div>"
                    "</div>"
                ),
            }
        ],
        css="""
:root{
  --bg:#ffffff;--fg:#1f2328;--muted:#6e7781;--primary:#1f6feb;--border:#eaeef2;
  --card:#f6f8fa;--tag:#eef2ff;--tag-border:#c7d2fe;--tag-fg:#3730a3;
  --memory:#fef3c7;--memory-border:#f59e0b;--memory-fg:#92400e;
  --easy:#dcfce7;--easy-b:#86efac;--easy-f:#166534;
  --med:#fef9c3;--med-b:#fde047;--med-f:#854d0e;
  --hard:#fee2e2;--hard-b:#fca5a5;--hard-f:#7f1d1d;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#0d1117;--fg:#e6edf3;--muted:#9ea7b3;--primary:#79c0ff;--border:#30363d;
    --card:#151b23;--tag:#1e293b;--tag-border:#334155;--tag-fg:#cbd5e1;
    --memory:#451a03;--memory-border:#f59e0b;--memory-fg:#fbbf24;
    --easy:#052e16;--easy-b:#14532d;--easy-f:#86efac;
    --med:#3f2d04;--med-b:#713f12;--med-f:#fde68a;
    --hard:#3f1d1d;--hard-b:#7f1d1d;--hard-f:#fecaca;
  }
} 
.card{
  background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Noto Sans SC',sans-serif;
  line-height:1.6;font-size:16px;
}
.wrap{max-width:760px;margin:0 auto;padding:12px 4px;}
.header{
  font-size:13px;color:var(--muted);letter-spacing:.12em;text-transform:uppercase;
  margin-bottom:16px;font-weight:600;
}
.card-type{
  display:inline-block;background:var(--primary);color:white;
  border-radius:999px;padding:4px 12px;font-size:12px;font-weight:600;
  margin-bottom:12px;
}
.card-type.memory{
  background:var(--memory);color:var(--memory-fg);border:1px solid var(--memory-border);
}
.question{
  font-size:24px;font-weight:700;margin:10px 0 4px;
}
.memory-hint{
  font-size:20px;font-weight:600;margin:12px 0;
  color:var(--memory-fg);background:var(--memory);
  padding:16px;border-radius:12px;border-left:4px solid var(--memory-border);
}
.memory-tip{
  font-size:14px;color:var(--muted);font-style:italic;
  margin-top:8px;padding:8px;background:var(--card);border-radius:6px;
}
.answer{
  font-size:18px;line-height:1.7;
}
.memory-answer{
  font-size:20px;font-weight:500;
  background:linear-gradient(135deg,var(--memory),rgba(245,158,11,0.1));
  border:2px solid var(--memory-border);border-radius:12px;
  padding:20px;margin:10px 0;
}
.memory-actions{
  display:flex;gap:12px;margin:16px 0;
}
.memory-btn{
  flex:1;padding:12px;border:none;border-radius:8px;font-size:16px;font-weight:600;
  cursor:pointer;transition:all 0.2s;
}
.memory-btn.easy{
  background:var(--easy);color:var(--easy-f);border:2px solid var(--easy-b);
}
.memory-btn.easy:hover{background:var(--easy-b);}
.memory-btn.hard{
  background:var(--hard);color:var(--hard-f);border:2px solid var(--hard-b);
}
.memory-btn.hard:hover{background:var(--hard-b);}
.sep{
  border:none;border-top:1px solid var(--border);margin:16px 0;
}
.meta-grid{
  display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0 8px;
}
@media (max-width:520px){.meta-grid{grid-template-columns:1fr;}}
.meta-item{
  display:flex;gap:8px;align-items:baseline;
  border-left:3px solid var(--border);padding-left:10px;
}
.label{color:var(--muted);font-size:13px;min-width:70px;font-weight:500;}
.value{font-size:14px;}
.tags .tag{
  display:inline-block;background:var(--tag);border:1px solid var(--tag-border);
  color:var(--tag-fg);border-radius:999px;padding:3px 10px;margin-right:8px;margin-bottom:6px;
  font-size:12px;font-weight:500;
}
.badge{
  display:inline-block;border-radius:6px;padding:3px 10px;font-size:12px;
  border:1px solid var(--border);font-weight:500;
}
.diff-easy{background:var(--easy);border-color:var(--easy-b);color:var(--easy-f)}
.diff-medium{background:var(--med);border-color:var(--med-b);color:var(--med-f)}
.diff-hard{background:var(--hard);border-color:var(--hard-b);color:var(--hard-f)}
.diff-unknown{background:var(--card);color:var(--muted)}
.evidence{margin-top:12px;}
.evidence summary{
  cursor:pointer;color:var(--primary);font-weight:500;padding:8px 0;
}
.evidence-body{
  margin-top:8px;background:var(--card);border:1px dashed var(--border);
  border-radius:8px;padding:12px;white-space:pre-wrap;font-size:14px;
}
""",
    )


def cloze_model() -> genanki.Model:
    return genanki.Model(
        model_id=998877665,
        name="Legal-Review-Cloze",
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
                "name": "填空记忆卡",
                "qfmt": (
                    "<div class='wrap'>"
                    "  <div class='header'>✏️ 法律填空卡片</div>"
                    "  <div class='card-type fill'>填空记忆</div>"
                    "  <div class='fill-instruction'>请填写空白处的正确答案</div>"
                    "  <div class='cloze'>{{cloze:Text}}</div>"
                    "</div>"
                ),
                "afmt": (
                    "{{FrontSide}}<hr class='sep'>"
                    "<div class='wrap'>"
                    "  <div class='fill-answer card-block'>完整答案已显示，请核对记忆</div>"
                    "  <div class='meta-grid'>"
                    "    <div class='meta-item'><span class='label'>📄 来源</span><span class='value'>{{SourceDoc}}</span></div>"
                    "    <div class='meta-item'><span class='label'>📍 位置</span><span class='value'>{{SourceLoc}}</span></div>"
                    "    <div class='meta-item'><span class='label'>⭐ 难度</span><span class='value'>{{Difficulty}}</span></div>"
                    "    <div class='meta-item'><span class='label'>🏷️ 标签</span><span class='value tags'>{{Tags}}</span></div>"
                    "  </div>"
                    "  <details class='evidence'><summary>📋 证据片段</summary><div class='evidence-body'>{{Evidence}}</div></details>"
                    "</div>"
                ),
            }
        ],
        css="""
:root{
  --bg:#ffffff;--fg:#1f2328;--muted:#6e7781;--primary:#1f6feb;--border:#eaeef2;
  --card:#f6f8fa;--tag:#eef2ff;--tag-border:#c7d2fe;--tag-fg:#3730a3;
  --fill:#dbeafe;--fill-border:#3b82f6;--fill-fg:#1e40af;
  --easy:#dcfce7;--easy-b:#86efac;--easy-f:#166534;
  --med:#fef9c3;--med-b:#fde047;--med-f:#854d0e;
  --hard:#fee2e2;--hard-b:#fca5a5;--hard-f:#7f1d1d;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#0d1117;--fg:#e6edf3;--muted:#9ea7b3;--primary:#79c0ff;--border:#30363d;
    --card:#151b23;--tag:#1e293b;--tag-border:#334155;--tag-fg:#cbd5e1;
    --fill:#1e3a8a;--fill-border:#60a5fa;--fill-fg:#93c5fd;
    --easy:#052e16;--easy-b:#14532d;--easy-f:#86efac;
    --med:#3f2d04;--med-b:#713f12;--med-f:#fde68a;
    --hard:#3f1d1d;--hard-b:#7f1d1d;--hard-f:#fecaca;
  }
} 
.card{
  background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Noto Sans SC',sans-serif;
  line-height:1.6;font-size:16px;
}
.wrap{max-width:760px;margin:0 auto;padding:12px 4px;}
.header{
  font-size:13px;color:var(--muted);letter-spacing:.12em;text-transform:uppercase;
  margin-bottom:16px;font-weight:600;
}
.card-type{
  display:inline-block;background:var(--primary);color:white;
  border-radius:999px;padding:4px 12px;font-size:12px;font-weight:600;
  margin-bottom:12px;
}
.card-type.fill{
  background:var(--fill);color:var(--fill-fg);border:1px solid var(--fill-border);
}
.fill-instruction{
  font-size:14px;color:var(--muted);font-style:italic;
  margin-bottom:12px;padding:8px;background:var(--card);border-radius:6px;
}
.cloze{
  font-size:20px;font-weight:600;line-height:1.8;
}
.cloze .cloze{
  color:var(--fill-fg);background:var(--fill);
  border:2px solid var(--fill-border);border-radius:4px;
  padding:2px 6px;font-weight:700;
}
.fill-answer{
  font-size:18px;font-weight:500;
  background:linear-gradient(135deg,var(--fill),rgba(59,130,246,0.1));
  border:2px solid var(--fill-border);border-radius:12px;
  padding:16px;margin:10px 0;
}
.sep{
  border:none;border-top:1px solid var(--border);margin:16px 0;
}
.meta-grid{
  display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0 8px;
}
@media (max-width:520px){.meta-grid{grid-template-columns:1fr;}}
.meta-item{
  display:flex;gap:8px;align-items:baseline;
  border-left:3px solid var(--border);padding-left:10px;
}
.label{color:var(--muted);font-size:13px;min-width:70px;font-weight:500;}
.value{font-size:14px;}
.tags .tag{
  display:inline-block;background:var(--tag);border:1px solid var(--tag-border);
  color:var(--tag-fg);border-radius:999px;padding:3px 10px;margin-right:8px;margin-bottom:6px;
  font-size:12px;font-weight:500;
}
.badge{
  display:inline-block;border-radius:6px;padding:3px 10px;font-size:12px;
  border:1px solid var(--border);font-weight:500;
}
.diff-easy{background:var(--easy);border-color:var(--easy-b);color:var(--easy-f)}
.diff-medium{background:var(--med);border-color:var(--med-b);color:var(--med-f)}
.diff-hard{background:var(--hard);border-color:var(--hard-b);color:var(--hard-f)}
.diff-unknown{background:var(--card);color:var(--muted)}
.evidence{margin-top:12px;}
.evidence summary{
  cursor:pointer;color:var(--primary);font-weight:500;padding:8px 0;
}
.evidence-body{
  margin-top:8px;background:var(--card);border:1px dashed var(--border);
  border-radius:8px;padding:12px;white-space:pre-wrap;font-size:14px;
}
""",
        model_type=genanki.Model.CLOZE,
    )
