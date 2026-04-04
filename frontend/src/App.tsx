import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import Trailer from './Trailer'
import './App.css'

type PromptType = 'scientific' | 'standard' | 'creative' | 'detailed' | 'chain_of_thought' | 'auto_detect' | 'with_confidence';
type BotState = 'idle' | 'thinking' | 'talking';
type LangCode = 'Arabic' | 'English';

interface HistoryItem { id: number; source: LangCode; target: LangCode; input: string; output: string; mode: PromptType; ts: number; }

/* ─────────────────────────────────────────
   ROBOT SVGs
───────────────────────────────────────── */
const ArabicBot = ({ state }: { state: BotState }) => {
  const isThinking = state === 'thinking';
  const isTalking = state === 'talking';

  return (
    <svg className="robot-body-svg" width="140" height="170" viewBox="0 0 130 170" fill="none">
      <defs>
        <radialGradient id="ar-glow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="rgba(0,255,153,0.3)" />
          <stop offset="100%" stopColor="transparent" />
        </radialGradient>
      </defs>
      {isThinking && <circle cx="65" cy="50" r="60" fill="url(#ar-glow)" style={{ animation: 'pulse 1.5s infinite' }} />}
      <g style={{ transformOrigin: '65px 16px', animation: isThinking ? 'think 0.3s infinite' : 'none' }}>
        <rect x="63" y="10" width="4" height="20" rx="2" fill="#00FF99" />
        <circle cx="65" cy="8" r="5" fill="#00FF99"><animate attributeName="opacity" values="1;0.4;1" dur="1s" repeatCount="indefinite" /></circle>
      </g>
      <rect x="18" y="30" width="94" height="70" rx="22" fill="#061210" stroke="#00FF99" strokeWidth="2" />
      <rect x="22" y="34" width="86" height="62" rx="20" fill="rgba(0,255,153,0.03)" />
      <rect x="28" y="45" width="74" height="26" rx="13" fill="#030807" stroke="rgba(0,255,153,0.3)" />
      <circle cx="44" cy="58" r="8" fill="#00FF99" filter="drop-shadow(0 0 5px #00FF99)" />
      <circle cx="86" cy="58" r="8" fill="#00FF99" filter="drop-shadow(0 0 5px #00FF99)" />
      <text x="65" y="42" textAnchor="middle" fill="#00FF99" fontSize="11" opacity="0.4" fontFamily="Cairo" fontWeight="bold">رايا</text>
      <g style={{ transformOrigin: '65px 82px', animation: isTalking ? 'talk 0.15s infinite' : 'none' }}>
        {[0, 1, 2, 3, 4].map(i => <rect key={i} x={42 + i * 11} y={80} width="4" height={isTalking ? 12 : 4} rx="2" fill="#00FF99" />)}
      </g>
      <rect x="52" y="100" width="26" height="8" rx="4" fill="#0d2920" stroke="#00FF99" strokeWidth="1" />
      <rect x="12" y="108" width="106" height="52" rx="18" fill="#0d2920" stroke="#00FF99" strokeWidth="2" />
      <path d="M30 115 Q65 105 100 115" stroke="rgba(0,255,153,0.2)" strokeWidth="1" fill="none" />
      {isThinking && [0, 1, 2].map(i => <circle key={i} cx={55 + i * 10} cy={134} r="4" fill="#00FF99" style={{ animation: `bounce 0.5s ${i * 0.1}s infinite` }} />)}
    </svg>
  );
};

const EnglishBot = ({ state }: { state: BotState }) => {
  const isThinking = state === 'thinking';
  const isTalking = state === 'talking';

  return (
    <svg className="robot-body-svg" width="140" height="170" viewBox="0 0 130 170" fill="none">
      <defs>
        <radialGradient id="en-glow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="rgba(0,191,255,0.3)" />
          <stop offset="100%" stopColor="transparent" />
        </radialGradient>
      </defs>
      {isThinking && <circle cx="65" cy="50" r="60" fill="url(#en-glow)" style={{ animation: 'pulse 1.5s infinite' }} />}
      <g style={{ transformOrigin: '65px 16px', animation: isThinking ? 'think 0.3s infinite' : 'none' }}>
        <rect x="50" y="12" width="3" height="15" rx="1.5" fill="#00BFFF" />
        <rect x="77" y="12" width="3" height="15" rx="1.5" fill="#00BFFF" />
        <circle cx="51.5" cy="8" r="4" fill="#00BFFF"><animate attributeName="opacity" values="1;0.4;1" dur="1s" repeatCount="indefinite" /></circle>
        <circle cx="78.5" cy="8" r="4" fill="#00BFFF"><animate attributeName="opacity" values="1;0.4;1" dur="0.8s" repeatCount="indefinite" /></circle>
      </g>
      <rect x="14" y="28" width="102" height="74" rx="14" fill="#06101a" stroke="#00BFFF" strokeWidth="2.5" />
      <rect x="20" y="34" width="90" height="62" rx="10" fill="rgba(0,191,255,0.04)" />
      <rect x="22" y="44" width="86" height="34" rx="6" fill="#02080f" stroke="rgba(0,191,255,0.2)" />
      <rect x="34" y="52" width="18" height="18" rx="4" fill="#00BFFF" filter="drop-shadow(0 0 6px #00BFFF)" />
      <rect x="78" y="52" width="18" height="18" rx="4" fill="#00BFFF" filter="drop-shadow(0 0 6px #00BFFF)" />
      <text x="65" y="40" textAnchor="middle" fill="#00BFFF" fontSize="10" opacity="0.4" fontFamily="Space Mono" fontWeight="bold">EN</text>
      <g style={{ transformOrigin: '65px 84px', animation: isTalking ? 'talk 0.15s infinite' : 'none' }}>
        <rect x="40" y="85" width="50" height={isTalking ? 8 : 2} rx="1" fill="#00BFFF" opacity="0.8" />
      </g>
      <rect x="50" y="102" width="30" height="8" rx="4" fill="#0d2440" stroke="#00BFFF" strokeWidth="1" />
      <rect x="14" y="110" width="102" height="48" rx="12" fill="#0d2440" stroke="#00BFFF" strokeWidth="2.5" />
      <circle cx="65" cy="134" r="10" fill="rgba(0,191,255,0.1)" stroke="#00BFFF" strokeWidth="1" />
      {isThinking && [0, 1, 2].map(i => <circle key={i} cx={55 + i * 10} cy={134} r="4" fill="#00BFFF" style={{ animation: `bounce 0.5s ${i * 0.1}s infinite` }} />)}
    </svg>
  );
};

/* ─────────────────────────────────────────
   MAIN APP
───────────────────────────────────────── */
export default function App() {
  const [inputText, setInputText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [status, setStatus] = useState<'idle' | 'translating' | 'error'>('idle');
  const [isSwapping, setIsSwapping] = useState(false);

  const [sourceLang, setSourceLang] = useState<LangCode>('Arabic');
  const targetLang = useMemo(() => sourceLang === 'Arabic' ? 'English' : 'Arabic', [sourceLang]);

  const [promptType, setPromptType] = useState<PromptType>('scientific');
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [toast, setToast] = useState('');
  const [showTrailer, setShowTrailer] = useState(true);
  const [showInfo, setShowInfo] = useState(false);
  const [infoLang, setInfoLang] = useState<'EN' | 'AR'>('EN');

  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    try {
      const saved = localStorage.getItem('translation_history_v2');
      if (saved) setHistory(JSON.parse(saved));
    } catch { }
  }, []);

  const showToastMsg = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  }, []);

  const handleTranslate = useCallback(async () => {
    if (!inputText.trim()) return;
    setStatus('translating');

    const cached = history.find(item => item.input.trim() === inputText.trim() && item.source === sourceLang && item.target === targetLang && item.mode === promptType);
    if (cached) {
      setTranslatedText(cached.output);
      setStatus('idle');
      return;
    }

    setTranslatedText('');
    let fullText = '';

    try {
      const abortController = new AbortController();
      const resp = await fetch('http://localhost:8000/stream-translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText, source_lang: sourceLang, target_lang: targetLang, prompt_type: promptType }),
        signal: abortController.signal
      });

      if (!resp.ok || !resp.body) throw new Error(`HTTP ${resp.status}`);

      const reader = resp.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        fullText += decoder.decode(value, { stream: true });
        setTranslatedText(fullText);
      }

      setStatus('idle');

      // Descriptive intelligent notification
      const wordCount = fullText.trim().split(/\s+/).length;
      if (targetLang === 'Arabic') {
        showToastMsg(`اكتملت الترجمة الذكية. تم تحليل ${wordCount} كلمة.`);
      } else {
        showToastMsg(`Smart translation complete. ${wordCount} words analyzed.`);
      }

      const newItem: HistoryItem = { id: Date.now(), source: sourceLang, target: targetLang, input: inputText, output: fullText.trim(), mode: promptType, ts: Date.now() };
      setHistory(prev => {
        const updated = [newItem, ...prev].slice(0, 20);
        localStorage.setItem('translation_history_v2', JSON.stringify(updated));
        return updated;
      });

    } catch (err) {
      setStatus('error');
      showToastMsg('Error: Check API server (port 8000)');
    }
  }, [inputText, sourceLang, targetLang, promptType, history, showToastMsg]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleTranslate(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [handleTranslate]);

  const swapLanguages = () => {
    setIsSwapping(true);
    // Smooth transition delay to match the fade-out/in
    setTimeout(() => {
      const currentInput = inputText;
      const currentOutput = translatedText;
      
      // Since targetLang is a useMemo based on sourceLang, 
      // we only need to flip sourceLang.
      setSourceLang(prev => (prev === 'Arabic' ? 'English' : 'Arabic'));
      setInputText(currentOutput);
      setTranslatedText(currentInput);
      
      setIsSwapping(false);
      
      // Auto-focus input after swap for efficiency
      setTimeout(() => inputRef.current?.focus(), 50);
    }, 400); // Matches CSS 0.4s animation
  };

  const copyToClipboard = () => {
    if (!translatedText) return;
    navigator.clipboard.writeText(translatedText);
    showToastMsg('Success! Copied to clipboard.');
  };

  const botStateInput: BotState = status === 'translating' ? 'thinking' : 'idle';
  const botStateOutput: BotState = status === 'translating' ? 'thinking' : (status === 'idle' && translatedText ? 'talking' : 'idle');
  const inputWordCount = inputText.trim() ? inputText.trim().split(/\s+/).length : 0;
  const outputWordCount = translatedText.trim() ? translatedText.trim().split(/\s+/).length : 0;

  return (
    <div className={`app-wrapper ${isSwapping ? 'swapping-view' : ''}`}>
      {showTrailer && <Trailer onComplete={() => setShowTrailer(false)} />}

      {showInfo && (
        <div className={`info-overlay ${infoLang === 'AR' ? 'rtl-view' : ''}`} onClick={() => setShowInfo(false)}>
          <div className="info-panel" onClick={e => e.stopPropagation()}>
            <div className="info-header" dir={infoLang === 'AR' ? 'rtl' : 'ltr'}>
              <div className="info-title-group">
                <span className="info-subtitle">{infoLang === 'EN' ? 'PROJECT DOSSIER' : 'ملف المشروع'}</span>
                <h2 className={`info-title ${infoLang === 'AR' ? 'arabic-font' : ''}`}>
                  {infoLang === 'EN' ? 'RAYYA AI INTELLIGENCE' : 'رايا للذكاء الاصطناعي'}
                </h2>
              </div>
              <div className="info-header-actions">
                <button className="lang-toggle-btn" onClick={() => setInfoLang(prev => prev === 'EN' ? 'AR' : 'EN')}>
                  {infoLang === 'EN' ? 'AR' : 'EN'}
                </button>
                <button className="close-info-btn" onClick={() => setShowInfo(false)}>×</button>
              </div>
            </div>

            <div className="info-body" dir={infoLang === 'AR' ? 'rtl' : 'ltr'}>
              <section className="info-section">
                <h3 className={`section-label ${infoLang === 'AR' ? 'arabic-font' : ''}`}>
                  {infoLang === 'EN' ? 'PROJECT MEMBERS' : 'أعضاء المشروع'}
                </h3>
                <div className="members-list">
                  <div className="member-row">
                    {infoLang === 'EN' ? <span>DJEFFAL Ramy</span> : <span className="arabic-font">جفال رامي</span>}
                  </div>
                  <div className="member-row">
                    {infoLang === 'EN' ? <span>MOULLA Yasmine</span> : <span className="arabic-font">مولا ياسمين</span>}
                  </div>
                  <div className="member-row">
                    {infoLang === 'EN' ? <span>DJINI Adem</span> : <span className="arabic-font">جيني آدم</span>}
                  </div>
                  <div className="member-row">
                    {infoLang === 'EN' ? <span>DAHAL Yousra</span> : <span className="arabic-font">دحال يسرى</span>}
                  </div>
                  <div className="member-row">
                    {infoLang === 'EN' ? <span>IHEDJADJEN Yacine Aksel</span> : <span className="arabic-font">إيهدجادجن ياسين أكسيل</span>}
                  </div>
                </div>
              </section>

              <section className="info-section">
                <h3 className={`section-label ${infoLang === 'AR' ? 'arabic-font' : ''}`}>
                  {infoLang === 'EN' ? 'MISSION GOAL' : 'هدف المهمة'}
                </h3>
                <p className={`info-para ${infoLang === 'AR' ? 'arabic-font' : ''}`}>
                  {infoLang === 'EN' ?
                    'Rayya.AI is designed to bridge the linguistic gap between Arabic and English using state-of-the-art Large Language Models. Our mission is to preserve cultural nuances while providing real-time, accurate, and creative translations.' :
                    'تم تصميم رايا للذكاء الاصطناعي لسد الفجوة اللغوية بين العربية والإنجليزية باستخدام أحدث نماذج اللغة الضخمة. مهمتنا هي الحفاظ على الفروق الثقافية الدقيقة مع توفير ترجمة فورية ودقيقة ومبدعة.'}
                </p>
              </section>

              <section className="info-section">
                <h3 className={`section-label ${infoLang === 'AR' ? 'arabic-font' : ''}`}>
                  {infoLang === 'EN' ? 'TECHNICAL STACK' : 'البيانات التقنية'}
                </h3>
                <div className="tech-grid">
                  <div className="tech-item">
                    <span>{infoLang === 'EN' ? 'ENGINE:' : 'المحرك:'}</span>
                    <strong className={infoLang === 'AR' ? 'arabic-font' : ''}>
                      {infoLang === 'EN' ? 'Gemini 2.5 Flash' : 'جيمناي 2.5 فلاش'}
                    </strong>
                  </div>
                  <div className="tech-item">
                    <span>{infoLang === 'EN' ? 'BACKEND:' : 'الخلفية:'}</span>
                    <strong className={infoLang === 'AR' ? 'arabic-font' : ''}>
                      {infoLang === 'EN' ? 'FastAPI / Python' : 'فاست أي بي آي / بايثون'}
                    </strong>
                  </div>
                  <div className="tech-item">
                    <span>{infoLang === 'EN' ? 'FRONTEND:' : 'الواجهة:'}</span>
                    <strong className={infoLang === 'AR' ? 'arabic-font' : ''}>
                      {infoLang === 'EN' ? 'React / Vite' : 'رياكت / فايت'}
                    </strong>
                  </div>
                  <div className="tech-item">
                    <span>{infoLang === 'EN' ? 'ARCHITECTURE:' : 'البنية:'}</span>
                    <strong className={infoLang === 'AR' ? 'arabic-font' : ''}>
                      {infoLang === 'EN' ? 'LLM Streaming' : 'بث النماذج اللغوية'}
                    </strong>
                  </div>
                </div>
              </section>
            </div>
            <div className="info-footer-status">
              {infoLang === 'EN' ? 'SYSTEM STATUS: OPTIMAL // VERSION 2.0.4' : 'حالة النظام: مثالية // الإصدار 2.0.4'}
            </div>
          </div>
        </div>
      )}

      <nav className="navbar">
        <div className="logo-container" onClick={() => setShowInfo(true)}>
          <div className="logo-badge">
            <svg width="46" height="46" viewBox="0 0 50 50" fill="none" className="main-logo-svg">
              <circle cx="25" cy="25" r="22" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
              <circle cx="25" cy="25" r="18" stroke="url(#logo-grad-main)" strokeWidth="2.5" strokeDasharray="80 40" className="logo-orbit-1" />
              <circle cx="25" cy="25" r="14" stroke="url(#logo-grad-main)" strokeWidth="1.5" strokeDasharray="30 20" className="logo-orbit-2" opacity="0.6" />
              <text x="25" y="32" textAnchor="middle" fill="white" fontSize="16" fontWeight="900" fontFamily="Cairo" style={{ textShadow: '0 0 15px rgba(0,255,153,0.5)' }}>رايا</text>
              <defs>
                <linearGradient id="logo-grad-main" x1="0" y1="0" x2="50" y2="50" gradientUnits="userSpaceOnUse">
                  <stop stopColor="var(--neon-green)" />
                  <stop offset="1" stopColor="var(--neon-blue)" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div className="logo-text-group">
            <h1 className="logo-main-text">RAYYA</h1>
            <div className="logo-sub-text">INTELLIGENT BRIDGE <span className="ai-highlight">.AI</span></div>
          </div>
        </div>
        <div className="nav-right">
          <button className="history-btn trailer-nav-btn" onClick={() => setShowTrailer(true)}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ marginRight: 6 }}><path d="M5 3l14 9-14 9V3z" /></svg>
            REPLAY TRAILER
          </button>
          <button className="history-btn" onClick={() => setShowHistory(!showHistory)}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: 6 }}><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            HISTORY ({history.length})
          </button>
        </div>
      </nav>

      <div className="translator-main">
        {/* INPUT PANEL */}
        <div className={`panel-container ${isSwapping ? 'fade-slide' : ''}`}>
          <div className="robot-header">
            <div className="robot-speech-bubble">
              {sourceLang === 'Arabic' ? <span dir="rtl">أدخل النص هنا</span> : 'Type text below'}
            </div>
            {sourceLang === 'Arabic' ? <ArabicBot state={botStateInput} /> : <EnglishBot state={botStateInput} />}
          </div>
          <div className={`glass-card ${sourceLang === 'Arabic' ? 'ar-indicator' : 'en-indicator'}`}>
            <div className="card-header" dir={sourceLang === 'Arabic' ? 'rtl' : 'ltr'}>
              <span className="lang-title">{sourceLang === 'Arabic' ? 'العربية · إدخال النص' : 'English Input'}</span>
              {inputText && (
                <button className="icon-btn" onClick={() => setInputText('')}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M18 6L6 18M6 6l12 12" /></svg>
                  {sourceLang === 'Arabic' ? 'مسح' : 'Clear'}
                </button>
              )}
            </div>
            <textarea
              ref={inputRef}
              className={`text-area ${sourceLang === 'Arabic' ? 'arabic-font' : ''}`}
              onChange={e => {
                setInputText(e.target.value);
                if (!e.target.value.trim()) setTranslatedText('');
              }}
            />
            <div className="card-footer" dir={sourceLang === 'Arabic' ? 'rtl' : 'ltr'}>
              <span>{inputText.length} chars</span>
              <span>{inputWordCount} {sourceLang === 'Arabic' ? 'كلمة' : 'words'}</span>
            </div>
          </div>
        </div>

        {/* CENTER ACTIONS */}
        <div className="center-actions">
          <button className={`swap-btn ${isSwapping ? 'rotate-animation' : ''}`} onClick={swapLanguages} title="Swap Languages">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M7 16V4m0 0L3 8m4-4l4 4M17 8v12m0 0l4-4m-4 4l-4-4" /></svg>
          </button>
          <button className="btn-primary" onClick={handleTranslate} disabled={status === 'translating' || !inputText.trim()} title="Ctrl + Enter">
            {status === 'translating' ? <div className="spinner" /> : (
              <>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
                <span>TRANSLATE</span>
              </>
            )}
          </button>
        </div>

        {/* OUTPUT PANEL */}
        <div className={`panel-container ${isSwapping ? 'fade-slide' : ''}`}>
          <div className="robot-header">
            <div className="robot-speech-bubble">
              {status === 'translating' ? (
                targetLang === 'Arabic' ? <span dir="rtl">جاري الترجمة...</span> : 'Translating...'
              ) : (
                translatedText ? (targetLang === 'Arabic' ? <span dir="rtl">إليك النتيجة!</span> : 'Result ready!') :
                  (targetLang === 'Arabic' ? <span dir="rtl">النتيجة تظهر هنا</span> : 'Output appears here')
              )}
            </div>
            {targetLang === 'Arabic' ? <ArabicBot state={botStateOutput} /> : <EnglishBot state={botStateOutput} />}
          </div>
          <div className={`glass-card ${targetLang === 'Arabic' ? 'ar-indicator' : 'en-indicator'}`}>
            <div className="card-header" dir={targetLang === 'Arabic' ? 'rtl' : 'ltr'}>
              <span className="lang-title">{targetLang === 'Arabic' ? 'العربية · الترجمة' : 'English Output'}</span>
              {translatedText && (
                <button className="icon-btn" onClick={copyToClipboard}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><rect x="9" y="9" width="13" height="13" rx="2" /><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" /></svg>
                  {targetLang === 'Arabic' ? 'نسخ' : 'Copy'}
                </button>
              )}
            </div>
            <div className="text-area-container" style={{ flex: 1, position: 'relative', minHeight: 200 }}>
              {status === 'translating' && (
                <div className="skeleton-loader">
                  <div className="skeleton-line" />
                  <div className="skeleton-line" />
                  <div className="skeleton-line" />
                </div>
              )}
              <textarea
                className={`text-area ${targetLang === 'Arabic' ? 'arabic-font' : ''} ${status === 'translating' ? 'loading' : ''}`}
                dir={targetLang === 'Arabic' ? 'rtl' : 'ltr'}
                placeholder={targetLang === 'Arabic' ? '...الترجمة ستظهر هنا' : 'Translation will appear here...'}
                value={translatedText}
                readOnly
              />
            </div>
            <div className="card-footer" dir={targetLang === 'Arabic' ? 'rtl' : 'ltr'}>
              <span>{translatedText.length} chars</span>
              <span>{outputWordCount} {targetLang === 'Arabic' ? 'كلمة' : 'words'}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="footer-actions">
        <select className="mode-select" value={promptType} onChange={e => setPromptType(e.target.value as PromptType)}>
          <option value="scientific">Academic / Scientific</option>
          <option value="standard">Standard Conversation</option>
          <option value="creative">Creative / Literary</option>
          <option value="detailed">Detailed Analysis</option>
        </select>
        <div style={{ color: 'var(--text-3)', fontSize: 11, fontWeight: 700, letterSpacing: 1 }}>POWERED BY RAYYA ARTIFICIAL INTELLIGENCE</div>
      </div>

      {showHistory && (
        <div className="history-panel">
          <div className="history-header">
            SAVED TRANSLATIONS
            <button className="icon-btn" onClick={() => setShowHistory(false)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M18 6L6 18M6 6l12 12" /></svg>
            </button>
          </div>
          <div className="history-list">
            {history.map(item => (
              <div key={item.id} className="history-item" onClick={() => {
                setSourceLang(item.source);
                setInputText(item.input);
                setTranslatedText(item.output);
                setShowHistory(false);
              }}>
                <div className="history-meta">{item.source} → {item.target}</div>
                <div style={{ color: 'var(--text-1)', fontSize: 13, marginBottom: 5, fontWeight: 600 }}>{item.input.substring(0, 40)}...</div>
                <div style={{ color: 'var(--text-2)', fontSize: 12 }}>{item.output.substring(0, 40)}...</div>
              </div>
            ))}
            {history.length === 0 && <div style={{ color: 'var(--text-3)', fontSize: 13, textAlign: 'center', padding: '40px 0' }}>Empty history.</div>}
            {history.length > 0 && (
              <button className="icon-btn" style={{ marginTop: 15, width: '100%', justifyContent: 'center', background: 'rgba(255,0,0,0.05)', color: '#ff4444' }} onClick={() => setHistory([])}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" style={{ marginRight: 6 }}><path d="M3 6h18m-2 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" /></svg>
                CLEAR ALL
              </button>
            )}
          </div>
        </div>
      )}
      {toast && (
        <div className={`toast ${targetLang === 'Arabic' ? 'arabic-font' : ''}`}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" style={{ marginRight: 8, color: 'var(--neon-green)' }}><path d="M20 6L9 17l-5-5" /></svg>
          {toast}
        </div>
      )}
    </div>
  )
}
