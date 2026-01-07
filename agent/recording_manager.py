"""
Recording Manager Module
Handles test execution recording, storage, and playback
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from playwright.sync_api import Page
import base64


class RecordingManager:
    """Manages test execution recordings"""
    
    def __init__(self, recordings_dir: str = 'recordings'):
        """
        Initialize recording manager
        
        Args:
            recordings_dir: Directory to store recordings
        """
        self.recordings_dir = recordings_dir
        os.makedirs(recordings_dir, exist_ok=True)
        self.current_recording = None
        self.recording_id = None
        
    def start_recording(self, test_name: str, url: str, instruction: str) -> str:
        """
        Start a new recording session
        
        Args:
            test_name: Name of the test
            url: Target URL
            instruction: Test instruction
            
        Returns:
            Recording ID
        """
        self.recording_id = f"rec_{int(time.time())}_{hash(test_name) % 10000}"
        
        self.current_recording = {
            'id': self.recording_id,
            'test_name': test_name,
            'url': url,
            'instruction': instruction,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': 0,
            'status': 'recording',
            'events': [],
            'screenshots': [],
            'metadata': {}
        }
        
        return self.recording_id
    
    def add_event(self, event_type: str, description: str, 
                  screenshot: Optional[str] = None, data: Optional[Dict] = None):
        """
        Add an event to the current recording
        
        Args:
            event_type: Type of event (action, navigation, assertion, error)
            description: Event description
            screenshot: Base64 encoded screenshot (optional)
            data: Additional event data (optional)
        """
        if not self.current_recording:
            return
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'description': description,
            'data': data or {},
            'screenshot_id': None
        }
        
        # Store screenshot separately if provided
        if screenshot:
            screenshot_id = f"screenshot_{len(self.current_recording['screenshots'])}"
            event['screenshot_id'] = screenshot_id
            self.current_recording['screenshots'].append({
                'id': screenshot_id,
                'data': screenshot,
                'timestamp': datetime.now().isoformat()
            })
        
        self.current_recording['events'].append(event)
    
    def capture_screenshot(self, page: Page) -> str:
        """
        Capture screenshot from page
        
        Args:
            page: Playwright page object
            
        Returns:
            Base64 encoded screenshot
        """
        try:
            screenshot_bytes = page.screenshot()
            return base64.b64encode(screenshot_bytes).decode('utf-8')
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            return None
    
    def stop_recording(self, status: str = 'completed', metadata: Optional[Dict] = None):
        """
        Stop the current recording
        
        Args:
            status: Final status (completed, failed, stopped)
            metadata: Additional metadata
        """
        if not self.current_recording:
            return
        
        start_time = datetime.fromisoformat(self.current_recording['start_time'])
        end_time = datetime.now()
        
        self.current_recording['end_time'] = end_time.isoformat()
        self.current_recording['duration'] = (end_time - start_time).total_seconds()
        self.current_recording['status'] = status
        
        if metadata:
            self.current_recording['metadata'].update(metadata)
        
        # Save recording to file
        self._save_recording()
        
        recording_id = self.recording_id
        self.current_recording = None
        self.recording_id = None
        
        return recording_id
    
    def _save_recording(self):
        """Save current recording to file"""
        if not self.current_recording:
            return
        
        filename = f"{self.recording_id}.json"
        filepath = os.path.join(self.recordings_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.current_recording, f, indent=2, ensure_ascii=False)
    
    def get_recording(self, recording_id: str) -> Optional[Dict]:
        """
        Get a specific recording
        
        Args:
            recording_id: Recording ID
            
        Returns:
            Recording data or None
        """
        filename = f"{recording_id}.json"
        filepath = os.path.join(self.recordings_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_recordings(self) -> List[Dict]:
        """
        List all recordings
        
        Returns:
            List of recording metadata
        """
        recordings = []
        
        for filename in os.listdir(self.recordings_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.recordings_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Return summary without full screenshot data
                        recordings.append({
                            'id': data['id'],
                            'test_name': data['test_name'],
                            'url': data['url'],
                            'start_time': data['start_time'],
                            'duration': data.get('duration', 0),
                            'status': data['status'],
                            'event_count': len(data.get('events', [])),
                            'screenshot_count': len(data.get('screenshots', []))
                        })
                except Exception as e:
                    print(f"Error reading recording {filename}: {e}")
        
        # Sort by start time (newest first)
        recordings.sort(key=lambda x: x['start_time'], reverse=True)
        return recordings
    
    def delete_recording(self, recording_id: str) -> bool:
        """
        Delete a recording
        
        Args:
            recording_id: Recording ID
            
        Returns:
            True if deleted, False otherwise
        """
        filename = f"{recording_id}.json"
        filepath = os.path.join(self.recordings_dir, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        
        return False
    
    def get_recording_video_path(self, recording_id: str) -> Optional[str]:
        """
        Get video file path for recording (if exists)
        
        Args:
            recording_id: Recording ID
            
        Returns:
            Video file path or None
        """
        video_filename = f"{recording_id}.webm"
        video_path = os.path.join(self.recordings_dir, video_filename)
        
        if os.path.exists(video_path):
            return video_path
        
        return None


# Singleton instance
_recording_manager = None

def get_recording_manager() -> RecordingManager:
    """Get singleton recording manager instance"""
    global _recording_manager
    if _recording_manager is None:
        _recording_manager = RecordingManager()
    return _recording_manager
