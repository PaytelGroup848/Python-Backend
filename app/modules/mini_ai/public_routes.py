from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.modules.mini_ai.entitlements import get_mini_ai_entitlements
from app.modules.mini_ai.lead_service import capture_lead
from app.modules.mini_ai.repository import mini_ai_repository
from app.modules.mini_ai.retrieval import generate_public_bot_answer
from app.modules.mini_ai.schemas import (
    PublicBotInfoResponse,
    PublicChatRequest,
    PublicChatResponse,
    PublicLeadCreateRequest,
)
from app.modules.mini_ai.security import (
    check_origin_allowed,
    enforce_public_rate_limit,
    get_client_ip,
)

router = APIRouter(prefix="/public", tags=["My Mini AI Public"])


def _cors_headers(origin: str | None) -> dict[str, str]:
    return {
        "Access-Control-Allow-Origin": origin or "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


async def _resolve_public_bot(db: AsyncSession, share_slug: str, request: Request):
    assistant = await mini_ai_repository.get_public_by_slug(db, share_slug.strip().lower())
    if assistant is None or assistant.owner_user_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    owner_entitlements = await get_mini_ai_entitlements(db, assistant.owner_user_id)
    if not owner_entitlements.allow_public_embed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This public assistant is paused until its owner upgrades to a Paid plan.",
        )

    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    if not check_origin_allowed(origin, referer, assistant.allowed_domains):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This domain is not authorized to embed this bot.",
        )
    return assistant, origin, owner_entitlements


@router.options("/bots/{share_slug}/chat")
@router.options("/bots/{share_slug}/leads")
async def public_bot_preflight(
    share_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    _, origin, _ = await _resolve_public_bot(db, share_slug, request)
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=_cors_headers(origin))


@router.get("/bots/{share_slug}", response_model=PublicBotInfoResponse)
async def get_public_bot_info(
    share_slug: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    assistant, origin, _ = await _resolve_public_bot(db, share_slug, request)
    for k, v in _cors_headers(origin).items():
        response.headers[k] = v
    return PublicBotInfoResponse(
        name=assistant.name,
        description=assistant.description,
        welcome_message=assistant.welcome_message,
        strict_rag=assistant.strict_rag,
    )


@router.post("/bots/{share_slug}/chat", response_model=PublicChatResponse)
async def public_bot_chat(
    share_slug: str,
    payload: PublicChatRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    assistant, origin, owner_entitlements = await _resolve_public_bot(db, share_slug, request)
    client_ip = get_client_ip(request)
    await enforce_public_rate_limit("chat", f"{share_slug}:{client_ip}", limit=20, window_seconds=60)
    await enforce_public_rate_limit("bot", share_slug, limit=120, window_seconds=60)
    month_key = datetime.now(timezone.utc).strftime("%Y-%m")
    await enforce_public_rate_limit(
        "owner_monthly",
        f"{assistant.owner_user_id}:{month_key}",
        limit=owner_entitlements.monthly_public_messages_limit,
        window_seconds=2678400,
    )

    result = await generate_public_bot_answer(
        db=db,
        assistant=assistant,
        message=payload.message,
        history=payload.history,
    )
    await db.commit()
    return JSONResponse(content=result.model_dump(), headers=_cors_headers(origin))


@router.post("/bots/{share_slug}/leads", status_code=status.HTTP_201_CREATED)
async def public_bot_capture_lead(
    share_slug: str,
    payload: PublicLeadCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    assistant, origin, _ = await _resolve_public_bot(db, share_slug, request)
    if assistant.owner_user_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    client_ip = get_client_ip(request)
    await enforce_public_rate_limit("lead", f"{share_slug}:{client_ip}", limit=10, window_seconds=60)

    await capture_lead(
        db=db,
        assistant_id=assistant.id,
        owner_user_id=assistant.owner_user_id,
        visitor_name=payload.visitor_name,
        visitor_contact=payload.visitor_contact,
        first_question=payload.first_question,
    )
    await db.commit()
    return JSONResponse(
        content={"status": "saved"},
        status_code=status.HTTP_201_CREATED,
        headers=_cors_headers(origin),
    )


_WIDGET_JS = r"""(function(){
  var s=document.currentScript;if(!s)return;
  var slug=s.getAttribute("data-bot");if(!slug)return;
  var base=(new URL(s.src)).origin;
  var color=s.getAttribute("data-color")||"#059669";
  var btn=document.createElement("button");
  btn.setAttribute("aria-label","Open AI Assistant");
  btn.textContent="Chat";
  btn.style.cssText="position:fixed;bottom:20px;right:20px;z-index:99999;background:"+color+";color:#fff;border:none;border-radius:999px;padding:12px 18px;font:600 14px system-ui,sans-serif;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.18)";
  var box=document.createElement("div");
  box.style.cssText="position:fixed;bottom:76px;right:20px;z-index:99999;width:340px;max-width:calc(100vw - 32px);height:460px;max-height:75vh;background:#fff;border:1px solid #e2e8f0;border-radius:16px;display:none;flex-direction:column;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,.2);font-family:system-ui,sans-serif";
  var hdr=document.createElement("div");
  hdr.style.cssText="background:"+color+";color:#fff;padding:12px 14px;display:flex;justify-content:space-between;align-items:center;font-weight:600;font-size:14px";
  var title=document.createElement("span");title.textContent="AI Assistant";
  var cls=document.createElement("button");cls.textContent="×";cls.setAttribute("aria-label","Close chat");
  cls.style.cssText="background:none;border:none;color:#fff;font-size:20px;cursor:pointer;line-height:1";
  hdr.appendChild(title);hdr.appendChild(cls);
  var log=document.createElement("div");
  log.style.cssText="flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px;background:#f8fafc;font-size:13px";
  var frm=document.createElement("form");
  frm.style.cssText="display:flex;gap:6px;padding:10px;border-top:1px solid #e2e8f0;background:#fff";
  var inp=document.createElement("input");inp.placeholder="Ask a question...";
  inp.style.cssText="flex:1;border:1px solid #cbd5e1;border-radius:10px;padding:8px 10px;font-size:13px;outline:none";
  var snd=document.createElement("button");snd.type="submit";snd.textContent="Send";
  snd.style.cssText="background:"+color+";color:#fff;border:none;border-radius:10px;padding:8px 12px;font-size:13px;font-weight:600;cursor:pointer";
  frm.appendChild(inp);frm.appendChild(snd);
  box.appendChild(hdr);box.appendChild(log);box.appendChild(frm);
  document.body.appendChild(btn);document.body.appendChild(box);
  function addMsg(role,txt){
    var m=document.createElement("div");
    m.textContent=txt;
    m.style.cssText="max-width:85%;padding:8px 11px;border-radius:12px;white-space:pre-wrap;word-break:break-word;"+(role==="user"?"align-self:flex-end;background:"+color+";color:#fff":"align-self:flex-start;background:#fff;color:#0f172a;border:1px solid #e2e8f0");
    log.appendChild(m);log.scrollTop=log.scrollHeight;return m;
  }
  var loaded=false,hist=[];
  function toggle(){
    var open=box.style.display==="flex";
    box.style.display=open?"none":"flex";
    if(!open&&!loaded){
      loaded=true;
      fetch(base+"/public/bots/"+encodeURIComponent(slug)).then(function(r){return r.ok?r.json():null}).then(function(d){
        if(d){title.textContent=d.name;if(d.welcome_message)addMsg("assistant",d.welcome_message);}
        else addMsg("assistant","Bot is currently unavailable.");
      }).catch(function(){addMsg("assistant","Unable to connect.");});
    }
    if(!open)inp.focus();
  }
  btn.onclick=toggle;cls.onclick=toggle;
  frm.onsubmit=function(e){
    e.preventDefault();var q=inp.value.trim();if(!q)return;inp.value="";
    addMsg("user",q);var wait=addMsg("assistant","Thinking...");snd.disabled=true;
    fetch(base+"/public/bots/"+encodeURIComponent(slug)+"/chat",{
      method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({message:q,history:hist.slice(-4)})
    }).then(function(r){return r.json().then(function(d){return {ok:r.ok,d:d}})}).then(function(res){
      wait.textContent=res.ok?res.d.answer:(res.d.detail||"Error generating reply.");
      if(res.ok){hist.push({role:"user",content:q},{role:"assistant",content:res.d.answer});}
    }).catch(function(){wait.textContent="Network error. Please retry.";}).finally(function(){snd.disabled=false;});
  };
})();"""


@router.get("/widget.js")
async def get_embed_widget_js():
    return Response(
        content=_WIDGET_JS,
        media_type="application/javascript",
        headers={"Cache-Control": "public, max-age=300"},
    )
