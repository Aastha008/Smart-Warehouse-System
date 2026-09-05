import React, { useState } from 'react';
import {
  Sliders,
  Bell,
  Volume2,
  Shield,
  Camera,
  Save,
  RotateCcw,
  CheckCircle2,
  Lock,
  EyeOff,
  Sparkles
} from 'lucide-react';
import { audioAlerts, requestNotificationPermission } from '../services/api';
import { RiskLevel } from '../types';

export default function Settings() {
  const [ppeThreshold, setPpeThreshold] = useState<number>(85);
  const [proximityDistance, setProximityDistance] = useState<number>(1.5);
  const [dropHeightSensitivity, setDropHeightSensitivity] = useState<number>(0.5);
  const [tiltTolerance, setTiltTolerance] = useState<number>(15);
  const [temporalWindow, setTemporalWindow] = useState<number>(30);

  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);
  const [soundVolume, setSoundVolume] = useState<number>(70);
  const [minAlertSeverity, setMinAlertSeverity] = useState<RiskLevel>('HIGH');
  const [browserNotifications, setBrowserNotifications] = useState<boolean>(false);

  const [faceBlurring, setFaceBlurring] = useState<boolean>(true);
  const [workerAnonymization, setWorkerAnonymization] = useState<boolean>(true);
  const [dataRetentionDays, setDataRetentionDays] = useState<number>(30);

  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  const handleTestSound = () => {
    audioAlerts.setVolume(soundVolume / 100);
    audioAlerts.playChime(minAlertSeverity);
  };

  const handleToggleBrowserNotifications = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const checked = e.target.checked;
    if (checked) {
      const granted = await requestNotificationPermission();
      setBrowserNotifications(granted);
    } else {
      setBrowserNotifications(false);
    }
  };

  const handleSave = () => {
    audioAlerts.setSoundEnabled(soundEnabled);
    audioAlerts.setVolume(soundVolume / 100);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  const handleReset = () => {
    setPpeThreshold(85);
    setProximityDistance(1.5);
    setDropHeightSensitivity(0.5);
    setTiltTolerance(15);
    setTemporalWindow(30);
    setSoundEnabled(true);
    setSoundVolume(70);
    setMinAlertSeverity('HIGH');
    setFaceBlurring(true);
    setWorkerAnonymization(true);
    setDataRetentionDays(30);
  };

  return (
    <div className="space-y-6 w-full">
      {/* Top Header & Save Button */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Safety Rules & Sensitivity Settings</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Configure camera sensitivity, drop and tilt alert thresholds, and audio warning chimes.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleReset}
            className="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 text-slate-700 dark:text-slate-200 rounded-lg text-xs font-bold transition-all shadow-2xs"
          >
            Reset
          </button>
          <button
            onClick={handleSave}
            className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold shadow-sm flex items-center gap-1.5 transition-all active:scale-95"
          >
            <Save className="w-4 h-4" /> Save Rules
          </button>
        </div>
      </div>

      {/* Success Feedback Banner */}
      {savedSuccess && (
        <div className="bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 rounded-xl p-4 shadow-xs flex items-center gap-3 text-emerald-800 dark:text-emerald-200 text-xs font-semibold animate-in fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span>Rules updated. New safety thresholds are active across all dock cameras.</span>
        </div>
      )}

      {/* Settings Section 1: CV & Temporal Behavior Parameters */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/90 dark:border-slate-800 p-6 shadow-xs space-y-6">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
          <div className="w-9 h-9 rounded-lg bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 flex items-center justify-center text-blue-600 dark:text-blue-400">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">Camera Sensitivity & Safety Triggers</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Adjust how strictly cameras flag drops, drags, and unstable stacks</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* YOLO Detection Confidence */}
          <div className="space-y-2 bg-slate-50 dark:bg-slate-800/60 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
            <div className="flex justify-between items-center text-xs">
              <label className="font-bold text-slate-800 dark:text-slate-200">Camera Detection Confidence</label>
              <span className="font-mono text-blue-600 dark:text-blue-400 font-bold">{ppeThreshold}%</span>
            </div>
            <input
              type="range"
              min={50}
              max={95}
              value={ppeThreshold}
              onChange={(e) => setPpeThreshold(Number(e.target.value))}
              className="w-full accent-blue-600 cursor-pointer"
            />
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Sensitivity threshold for detecting warehouse workers, equipment, pallets, and cartons.
            </p>
          </div>

          {/* Proximity Distance Threshold */}
          <div className="space-y-2 bg-slate-50 dark:bg-slate-800/60 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
            <div className="flex justify-between items-center text-xs">
              <label className="font-bold text-slate-800">Pedestrian Proximity Margin</label>
              <span className="font-mono text-orange-600 font-bold">{proximityDistance} m</span>
            </div>
            <input
              type="range"
              min={0.5}
              max={3.5}
              step={0.1}
              value={proximityDistance}
              onChange={(e) => setProximityDistance(Number(e.target.value))}
              className="w-full accent-orange-600 cursor-pointer"
            />
            <p className="text-[11px] text-slate-500">
              Trigger alert when pedestrian is within this radius of moving equipment.
            </p>
          </div>

          {/* Drop Height Sensitivity */}
          <div className="space-y-2 bg-slate-50 dark:bg-slate-800/60 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
            <div className="flex justify-between items-center text-xs">
              <label className="font-bold text-slate-800 dark:text-slate-200">Drop Height Sensitivity</label>
              <span className="font-mono text-rose-600 font-bold">{dropHeightSensitivity} m</span>
            </div>
            <input
              type="range"
              min={0.2}
              max={1.5}
              step={0.05}
              value={dropHeightSensitivity}
              onChange={(e) => setDropHeightSensitivity(Number(e.target.value))}
              className="w-full accent-rose-500 cursor-pointer"
            />
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Downward displacement threshold to classify vertical movement as product drop.
            </p>
          </div>

          {/* Stacking Tilt Tolerance */}
          <div className="space-y-2 bg-slate-50 dark:bg-slate-800/60 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
            <div className="flex justify-between items-center text-xs">
              <label className="font-bold text-slate-800 dark:text-slate-200">Stack Tilt Angular Tolerance</label>
              <span className="font-mono text-amber-600 font-bold">{tiltTolerance}°</span>
            </div>
            <input
              type="range"
              min={5}
              max={30}
              value={tiltTolerance}
              onChange={(e) => setTiltTolerance(Number(e.target.value))}
              className="w-full accent-amber-500 cursor-pointer"
            />
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Maximum allowable lateral angular tilt before flagging unstable pallet stacking.
            </p>
          </div>
        </div>
      </div>

      {/* Settings Section 2: Audio Chimes & Alert Notifications */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/90 dark:border-slate-800 p-6 shadow-xs space-y-6">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
          <div className="w-9 h-9 rounded-lg bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800 flex items-center justify-center text-amber-600 dark:text-amber-400">
            <Bell className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">Audio Chimes & Notification Rules</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Web Audio API chime synthesizer and notification triggers</p>
          </div>
        </div>

        <div className="space-y-4">
          {/* Sound alert master switch & test */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-200 dark:border-slate-700 gap-4">
            <div className="flex items-center gap-3">
              <Volume2 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <div>
                <span className="text-xs font-bold text-slate-900 dark:text-white block">Web Audio Alert Chimes</span>
                <span className="text-[11px] text-slate-500 dark:text-slate-400">
                  Plays synthesized harmonic audio tones on high/critical anomalies
                </span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={handleTestSound}
                className="px-3.5 py-1.5 rounded-lg bg-white dark:bg-slate-800 hover:bg-slate-100 text-slate-700 dark:text-slate-200 text-xs font-bold transition-colors border border-slate-200 dark:border-slate-700 shadow-2xs"
              >
                Test Sound Chime
              </button>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={soundEnabled}
                  onChange={(e) => setSoundEnabled(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-200 dark:bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600" />
              </label>
            </div>
          </div>

          {/* Volume Slider */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2 bg-slate-50 dark:bg-slate-800/60 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
              <div className="flex justify-between items-center text-xs">
                <label className="font-bold text-slate-800 dark:text-slate-200">Chime Volume</label>
                <span className="font-mono text-slate-500 dark:text-slate-400">{soundVolume}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={soundVolume}
                onChange={(e) => setSoundVolume(Number(e.target.value))}
                className="w-full accent-slate-900 cursor-pointer"
              />
            </div>

            <div className="space-y-2 bg-slate-50 dark:bg-slate-800/60 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
              <div className="flex justify-between items-center text-xs">
                <label className="font-bold text-slate-800 dark:text-slate-200">Minimum Severity for Audio Alert</label>
                <span className="font-mono text-amber-700 dark:text-amber-400 font-bold">{minAlertSeverity}</span>
              </div>
              <select
                value={minAlertSeverity}
                onChange={(e) => setMinAlertSeverity(e.target.value as RiskLevel)}
                className="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="CRITICAL">CRITICAL Only</option>
                <option value="HIGH">HIGH & CRITICAL</option>
                <option value="MEDIUM">MEDIUM, HIGH & CRITICAL</option>
              </select>
            </div>
          </div>

          {/* HTML5 Browser Notification Toggle */}
          <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-200 dark:border-slate-700">
            <div>
              <span className="text-xs font-bold text-slate-900 dark:text-white block">HTML5 Browser Notifications</span>
              <span className="text-[11px] text-slate-500 dark:text-slate-400">
                Push desktop alerts when anomalies are detected even when dashboard tab is in background
              </span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={browserNotifications}
                onChange={handleToggleBrowserNotifications}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-200 dark:bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600" />
            </label>
          </div>
        </div>
      </div>

      {/* Settings Section 3: Responsible AI & Privacy */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/90 dark:border-slate-800 p-6 shadow-xs space-y-6">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
          <div className="w-9 h-9 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">Responsible AI & Worker Privacy</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Ethical AI safeguards, privacy preservation, and data minimization</p>
          </div>
        </div>

        <div className="space-y-3">
          <label className="flex items-start gap-3 p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-200 dark:border-slate-700 cursor-pointer hover:bg-slate-100/60 transition-colors">
            <input
              type="checkbox"
              checked={faceBlurring}
              onChange={(e) => setFaceBlurring(e.target.checked)}
              className="mt-0.5 w-4 h-4 text-blue-600 rounded accent-blue-600"
            />
            <div>
              <span className="text-xs font-bold text-slate-900 dark:text-white block">Automated Face Blurring</span>
              <span className="text-[11px] text-slate-500 dark:text-slate-400">
                Immediately anonymize worker facial features in recorded video storage clips.
              </span>
            </div>
          </label>

          <label className="flex items-start gap-3 p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-200 dark:border-slate-700 cursor-pointer hover:bg-slate-100/60 transition-colors">
            <input
              type="checkbox"
              checked={workerAnonymization}
              onChange={(e) => setWorkerAnonymization(e.target.checked)}
              className="mt-0.5 w-4 h-4 text-blue-600 rounded accent-blue-600"
            />
            <div>
              <span className="text-xs font-bold text-slate-900 dark:text-white block">Behavior-Only Tracking (No Biometrics)</span>
              <span className="text-[11px] text-slate-500 dark:text-slate-400">
                Track kinetic motions and objects without biometric profiling or individual worker tracking.
              </span>
            </div>
          </label>

          <div className="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-200 dark:border-slate-700">
            <div>
              <span className="text-xs font-bold text-slate-900 dark:text-white block">Video Data Retention Window</span>
              <span className="text-[11px] text-slate-500 dark:text-slate-400">
                Auto-purge non-incident video clips after the specified duration
              </span>
            </div>
            <select
              value={dataRetentionDays}
              onChange={(e) => setDataRetentionDays(Number(e.target.value))}
              className="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value={7}>7 Days</option>
              <option value={14}>14 Days</option>
              <option value={30}>30 Days</option>
              <option value={90}>90 Days</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
