import React, { useState, useEffect } from 'react';
import './Trailer.css';

interface TrailerProps {
  onComplete: () => void;
}

const Trailer: React.FC<TrailerProps> = ({ onComplete }) => {
  const [step, setStep] = useState<'english' | 'connecting' | 'arabic' | 'team' | 'exiting' | 'done'>('english');
  const [visibleWords, setVisibleWords] = useState<number>(0);
  const [progress, setProgress] = useState(0);
  const [showSkip, setShowSkip] = useState(false);

  const englishText = "Rayya AI: Breaking language barriers, connecting cultures, and uniting worlds through intelligence.";
  const arabicText = "رايا للذكاء الاصطناعي: كسر حواجز اللغة، ربط الثقافات، وتوحيد العوالم عبر التكنولوجيا الذكية.";

  const teamMembers = [
    { en: "DJEFFAL Ramy", ar: "جفال رامي" },
    { en: "MOULLA Yasmine", ar: "مولا ياسمين" },
    { en: "DJINI Adem", ar: "جيني آدم" },
    { en: "DAHAL Yousra", ar: "دحال يسرى" },
    { en: "IHEDJADJEN Yacine Aksel", ar: "إيهدجادجن ياسين أكسيل" }
  ];

  const englishWords = englishText.split(' ');
  const arabicWords = arabicText.split(' ');

  useEffect(() => {
    // Total steps calculation for progress bar
    const totalWords = englishWords.length + arabicWords.length + teamMembers.length + 1; // +1 for connecting step
    let currentCount = 0;

    if (step === 'english') currentCount = visibleWords;
    else if (step === 'connecting') currentCount = englishWords.length + 0.5;
    else if (step === 'arabic') currentCount = englishWords.length + 1 + visibleWords;
    else if (step === 'team') currentCount = englishWords.length + 1 + arabicWords.length + visibleWords;
    else if (step === 'exiting') currentCount = totalWords;

    setProgress((currentCount / totalWords) * 100);
  }, [step, visibleWords, englishWords.length, arabicWords.length, teamMembers.length]);

  useEffect(() => {
    const initTimer = setTimeout(() => {
      if (step === 'english') {
        if (visibleWords < englishWords.length) {
          const timer = setTimeout(() => setVisibleWords(prev => prev + 1), 120); // Calmer (was 95)
          return () => clearTimeout(timer);
        } else {
          const nextTimer = setTimeout(() => setStep('connecting'), 1000); // Calmer (was 800)
          return () => clearTimeout(nextTimer);
        }
      } else if (step === 'connecting') {
        const connTimer = setTimeout(() => {
          setStep('arabic');
          setVisibleWords(0);
        }, 1500); // Calmer (was 1300)
        return () => clearTimeout(connTimer);
      } else if (step === 'arabic') {
        if (visibleWords < arabicWords.length) {
          const timer = setTimeout(() => setVisibleWords(prev => prev + 1), 130); // Calmer (was 110)
          return () => clearTimeout(timer);
        } else {
          const nextTimer = setTimeout(() => {
            setStep('team');
            setVisibleWords(0);
          }, 800); // Moderated (was 600)
          return () => clearTimeout(nextTimer);
        }
      } else if (step === 'team') {
        if (visibleWords < teamMembers.length) {
          const timer = setTimeout(() => setVisibleWords(prev => prev + 1), 450); // Moderated (was 300)
          return () => clearTimeout(timer);
        } else {
          const exitTimer = setTimeout(() => setStep('exiting'), 2200); // Moderated (was 1800)
          return () => clearTimeout(exitTimer);
        }
      } else if (step === 'exiting') {
         const doneTimer = setTimeout(() => {
            setStep('done');
            onComplete();
         }, 1000); // Moderated (was 800)
         return () => clearTimeout(doneTimer);
      }
    }, 200); // Moderated (was 100)
    return () => clearTimeout(initTimer);
  }, [step, visibleWords, englishWords.length, arabicWords.length, teamMembers.length, onComplete]);

  useEffect(() => {
    const timer = setTimeout(() => setShowSkip(true), 3000); // Show skip after 3s
    return () => clearTimeout(timer);
  }, []);

  const handleSkip = () => {
    setStep('exiting');
  };

  if (step === 'done') return null;

  return (
    <div className={`trailer-overlay ${step === 'exiting' ? 'fade-out' : ''}`}>
      {showSkip && step !== 'exiting' && (
        <button className="skip-trailer-btn" onClick={handleSkip}>
          SKIP TRAILER
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" style={{ marginLeft: 8 }}><path d="M5 4l10 8-10 8V4zM19 5v14" /></svg>
        </button>
      )}
      <div className="trailer-progress-container">
        <div className="trailer-progress-bar" style={{ width: `${progress}%` }}></div>
      </div>

      <div className="trailer-content">
        <div className="neural-grid"></div>
        <div className="trailer-glitch-layer"></div>

        <div className="trailer-text-container">
          {step === 'english' && (
            <div className="trailer-text en-trailer">
              {englishWords.map((word, i) => (
                <span key={i} className={`trailer-word ${i < visibleWords ? 'visible' : ''}`}>
                  {word}{' '}
                </span>
              ))}
            </div>
          )}

          {step === 'connecting' && (
            <div className="trailer-ai-status">
              <div className="simple-sync-flash">
                 <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="var(--neon-blue)" strokeWidth="3" className="sync-arrow-flash">
                    <path d="M5 12h14m-7-7l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
                 </svg>
                 <div className="sync-loading-dots">...</div>
              </div>
              <div className="ai-status-text">
                <span className="minimalist-sync">TRANSLATE</span>
              </div>
            </div>
          )}

          {step === 'arabic' && (
            <div className="trailer-text ar-trailer" dir="rtl">
              {arabicWords.map((word, i) => (
                <span key={i} className={`trailer-word ${i < visibleWords ? 'visible' : ''}`}>
                  {word}{' '}
                </span>
              ))}
            </div>
          )}

          {step === 'team' && (
            <div className="team-reveal">
              <div className="team-label">CRAFTED WITH PRECISION BY</div>
              <div className="team-grid">
                {teamMembers.map((member, i) => (
                  <div key={i} className={`team-card ${i < visibleWords ? 'visible' : ''}`}>
                    <div className="team-en">{member.en}</div>
                    <div className="team-ar" dir="rtl">{member.ar}</div>
                    <div className="team-glow"></div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Trailer;
