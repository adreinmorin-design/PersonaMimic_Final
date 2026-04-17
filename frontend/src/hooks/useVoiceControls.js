import { useEffect, useRef, useState } from 'react';
import { api } from '../lib/api';

const LISTEN_WINDOW_MS = 4000;
const DEFAULT_TRAINING_SCRIPT = 'My voice is my password. PersonaMimic recognizes me as the secure operator of this studio.';

function stopStream(stream) {
  stream?.getTracks().forEach((track) => track.stop());
}

function playAudio(url) {
  if (url) {
    new Audio(url).play();
  }
}

export function useVoiceControls({ username, onAutonomousReply, onSentinelUnlock }) {
  const [isRecording, setIsRecording] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState('');
  const [trainingScript, setTrainingScript] = useState('');

  const activeModeRef = useRef(null);
  const activeStreamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const autonomousReplyRef = useRef(onAutonomousReply);
  const sentinelUnlockRef = useRef(onSentinelUnlock);

  useEffect(() => {
    autonomousReplyRef.current = onAutonomousReply;
  }, [onAutonomousReply]);

  useEffect(() => {
    sentinelUnlockRef.current = onSentinelUnlock;
  }, [onSentinelUnlock]);

  useEffect(() => () => {
    activeModeRef.current = null;
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== 'inactive') {
      try {
        recorder.stop();
      } catch (e) {
        console.warn('Recorder stop failed:', e);
      }
    }
    stopStream(activeStreamRef.current);
  }, []);

  const endSession = ({ clearStatus = false } = {}) => {
    activeModeRef.current = null;
    setIsRecording(false);
    setTrainingScript('');
    if (clearStatus) {
      setVoiceStatus('');
    }

    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== 'inactive') {
      try {
        recorder.stop();
      } catch (e) {
        console.warn('Recorder stop failed:', e);
      }
    }
    stopStream(activeStreamRef.current);
    activeStreamRef.current = null;
    mediaRecorderRef.current = null;
  };

  const startTimedRecording = (stream, mode, onStop) => {
    const recorder = new MediaRecorder(stream);
    const chunks = [];

    mediaRecorderRef.current = recorder;
    recorder.ondataavailable = (event) => {
      chunks.push(event.data);
    };

    recorder.onstop = async () => {
      if (activeModeRef.current !== mode || !chunks.length) {
        return;
      }

      const audioBlob = new Blob(chunks, { type: 'audio/wav' });
      await onStop(audioBlob, stream);
    };

    recorder.start();
    window.setTimeout(() => {
      if (recorder.state !== 'inactive') {
        recorder.stop();
      }
    }, LISTEN_WINDOW_MS);
  };

  const startVoiceRegistration = async () => {
    if (activeModeRef.current === 'registration') {
      setIsRecording(false);
      setTrainingScript('');
      mediaRecorderRef.current?.stop();
      stopStream(activeStreamRef.current);
      return;
    }

    endSession({ clearStatus: true });

    // 1. Fetch training script
    try {
      const response = await api.get('/auth/voice-scripts');
      setTrainingScript(response.data.script || DEFAULT_TRAINING_SCRIPT);
    } catch {
      setTrainingScript(DEFAULT_TRAINING_SCRIPT);
    }

    // 2. Initialize Microphone
    setVoiceStatus('Initializing Microphone...');
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      endSession();
      setVoiceStatus('Microphone access denied or backend offline.');
      return;
    }

    const recorder = new MediaRecorder(stream);
    const chunks = [];
    activeModeRef.current = 'registration';
    activeStreamRef.current = stream;
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = (event) => chunks.push(event.data);
    recorder.onstop = async () => {
      const audioBlob = new Blob(chunks, { type: 'audio/wav' });
      const formData = new FormData();
      formData.append('file', audioBlob, 'voice.wav');

      try {
        setVoiceStatus('Encrypting Neural Voiceprint (Analyzing audio)...');
        await api.post(`/auth/voice-register?username=${encodeURIComponent(username || 'Dre')}`, formData);
        setVoiceStatus('Master Voice Registered!');
      } catch (error) {
        setVoiceStatus(error.response?.data?.detail || 'Voice error (Ensure you speak clearly).');
      } finally {
        endSession();
        window.setTimeout(() => setVoiceStatus(''), 3000);
      }
    };

    recorder.start();
    setIsRecording(true);
    setVoiceStatus('Recording... Read the script above, then click the Mic to stop.');
  };

  const startSentinelVoiceAuth = async () => {
    if (isRecording) {
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      activeModeRef.current = 'sentinel';
      activeStreamRef.current = stream;
      setIsRecording(true);
      setVoiceStatus('Neural Hearing Active... Continuous scan running.');

      const verifyLoop = () => {
        if (activeModeRef.current !== 'sentinel' || !stream.active) {
          return;
        }

        startTimedRecording(stream, 'sentinel', async (audioBlob) => {
          const formData = new FormData();
          formData.append('file', audioBlob, 'voice.wav');

          try {
            const response = await api.post('/auth/voice-verify', formData);
            if (response.data.sentinel_key) {
              stopStream(stream);
              endSession();
              sentinelUnlockRef.current?.(response.data.sentinel_key);
              return;
            }
          } catch {
            // Continuous verification intentionally suppresses loop noise.
          }

          verifyLoop();
        });
      };

      verifyLoop();
    } catch {
      endSession();
      setVoiceStatus('Microphone access denied.');
    }
  };

  const toggleAutonomousChat = async () => {
    if (activeModeRef.current === 'autonomous') {
      endSession({ clearStatus: true });
      return;
    }

    endSession({ clearStatus: true });

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      activeModeRef.current = 'autonomous';
      activeStreamRef.current = stream;
      setIsRecording(true);
      setVoiceStatus('Neural Hearing Sync Active...');

      const runLoop = () => {
        if (activeModeRef.current !== 'autonomous' || !stream.active) {
          return;
        }

        startTimedRecording(stream, 'autonomous', async (audioBlob) => {
          const formData = new FormData();
          formData.append('file', audioBlob, 'voice.wav');

          try {
            const response = await api.post('/voice/autonomous-chat', formData);
            if (response.data.status === 'success') {
              autonomousReplyRef.current?.({
                text: response.data.text,
                response: response.data.response,
                audioUrl: response.data.audio_url,
              });
              playAudio(response.data.audio_url);
            }
          } catch (error) {
            console.error('Autonomous loop error:', error);
          }

          runLoop();
        });
      };

      runLoop();
    } catch {
      endSession();
      setVoiceStatus('Microphone access needed for Neural Hearing.');
    }
  };

  return {
    isRecording,
    voiceStatus,
    trainingScript,
    startVoiceRegistration,
    startSentinelVoiceAuth,
    toggleAutonomousChat,
  };
}
