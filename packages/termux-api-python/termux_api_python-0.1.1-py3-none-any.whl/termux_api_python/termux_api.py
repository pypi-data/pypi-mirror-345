#!/usr/bin/env python3
"""
Termux API Python Wrapper

This module provides a Python interface to the Termux API commands.
"""

import subprocess
import json
import shlex
import os
from typing import List, Dict, Union, Optional, Any


class TermuxAPI:
    """Wrapper class for Termux API commands."""

    @staticmethod
    def _run_command(command: List[str], input_data: str = None) -> str:
        """Run a command and return its output."""
        try:
            if input_data:
                result = subprocess.run(
                    command,
                    input=input_data.encode(),
                    capture_output=True,
                    text=True,
                    check=True
                )
            else:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True
                )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with exit code {e.returncode}: {e.stderr}"
            raise RuntimeError(error_msg)

    @staticmethod
    def _parse_json_output(output: str) -> Any:
        """Parse JSON output from a command."""
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return output

    def battery_status(self) -> Dict:
        """Get battery status information."""
        output = self._run_command(["termux-battery-status"])
        return self._parse_json_output(output)

    def brightness(self, level: Union[int, str]) -> None:
        """
        Set the screen brightness.
        
        Args:
            level: Brightness level (0-255) or 'auto'
        """
        self._run_command(["termux-brightness", str(level)])

    def call_log(self, limit: int = None, offset: int = None) -> List[Dict]:
        """
        Get the call log.
        
        Args:
            limit: Maximum number of entries to return
            offset: Offset from which to start returning entries
        """
        cmd = ["termux-call-log"]
        if limit is not None:
            cmd.extend(["-l", str(limit)])
        if offset is not None:
            cmd.extend(["-o", str(offset)])
        output = self._run_command(cmd)
        return self._parse_json_output(output)

    def camera_info(self) -> List[Dict]:
        """Get information about device cameras."""
        output = self._run_command(["termux-camera-info"])
        return self._parse_json_output(output)

    def camera_photo(self, output_file: str, camera_id: int = None) -> None:
        """
        Take a photo and save it to a file.
        
        Args:
            output_file: Path to save the photo
            camera_id: ID of the camera to use
        """
        cmd = ["termux-camera-photo"]
        if camera_id is not None:
            cmd.extend(["-c", str(camera_id)])
        cmd.append(output_file)
        self._run_command(cmd)

    def clipboard_get(self) -> str:
        """Get the system clipboard text."""
        return self._run_command(["termux-clipboard-get"])

    def clipboard_set(self, text: str) -> None:
        """
        Set the system clipboard text.
        
        Args:
            text: Text to set in the clipboard
        """
        self._run_command(["termux-clipboard-set"], input_data=text)

    def contact_list(self) -> List[Dict]:
        """Get a list of contacts."""
        output = self._run_command(["termux-contact-list"])
        return self._parse_json_output(output)

    def dialog(self, dialog_type: str, **kwargs) -> Dict:
        """
        Show a dialog.
        
        Args:
            dialog_type: Type of dialog ('confirm', 'checkbox', 'counter', 'date', 'radio', 'sheet', 'speech', 'spinner', 'text', 'time')
            **kwargs: Additional arguments for the dialog
        """
        cmd = ["termux-dialog", dialog_type]
        for key, value in kwargs.items():
            cmd.extend([f"--{key.replace('_', '-')}", str(value)])
        output = self._run_command(cmd)
        return self._parse_json_output(output)

    def download(self, url: str, title: str = None, description: str = None, path: str = None) -> None:
        """
        Download a file.
        
        Args:
            url: URL to download
            title: Title for the download notification
            description: Description for the download notification
            path: Path to save the downloaded file
        """
        cmd = ["termux-download", url]
        if title:
            cmd.extend(["-t", title])
        if description:
            cmd.extend(["-d", description])
        if path:
            cmd.extend(["-p", path])
        self._run_command(cmd)

    def fingerprint(self, title: str = None, description: str = None) -> Dict:
        """
        Authenticate with a fingerprint.
        
        Args:
            title: Title for the fingerprint dialog
            description: Description for the fingerprint dialog
        """
        cmd = ["termux-fingerprint"]
        if title:
            cmd.extend(["-t", title])
        if description:
            cmd.extend(["-d", description])
        output = self._run_command(cmd)
        return self._parse_json_output(output)

    def infrared_frequencies(self) -> List[int]:
        """Get the infrared frequencies supported by the device."""
        output = self._run_command(["termux-infrared-frequencies"])
        return self._parse_json_output(output)

    def infrared_transmit(self, frequency: int, pattern: List[int]) -> None:
        """
        Transmit an infrared pattern.
        
        Args:
            frequency: Frequency to transmit at
            pattern: Pattern to transmit
        """
        pattern_str = ",".join(map(str, pattern))
        self._run_command(["termux-infrared-transmit", "-f", str(frequency), "-p", pattern_str])

    def location(self, provider: str = None, request: str = None) -> Dict:
        """
        Get the device location.
        
        Args:
            provider: Location provider ('gps', 'network', 'passive')
            request: Request type ('once', 'updates', 'last')
        """
        cmd = ["termux-location"]
        if provider:
            cmd.extend(["-p", provider])
        if request:
            cmd.extend(["-r", request])
        output = self._run_command(cmd)
        return self._parse_json_output(output)

    def media_player(self, command: str, file: str = None) -> None:
        """
        Control the media player.
        
        Args:
            command: Command to execute ('play', 'pause', 'stop', 'info')
            file: File to play (only for 'play' command)
        """
        cmd = ["termux-media-player", command]
        if command == "play" and file:
            cmd.append(file)
        self._run_command(cmd)

    def media_scan(self, file: str) -> None:
        """
        Scan a file to add it to the media content provider.
        
        Args:
            file: File to scan
        """
        self._run_command(["termux-media-scan", file])

    def microphone_record(self, file: str = None, limit: int = None, 
                         encoder: str = None, bitrate: int = None, 
                         rate: int = None, count: int = None) -> Union[Dict, None]:
        """
        Record audio from the microphone.
        
        Args:
            file: File to save the recording to
            limit: Time limit in seconds (0 for unlimited)
            encoder: Audio encoder ('aac', 'amr_wb', 'amr_nb', 'opus')
            bitrate: Bitrate in kbps
            rate: Sampling rate in Hz
            count: Channel count
        """
        cmd = ["termux-microphone-record"]
        if file:
            cmd.extend(["-f", file])
        if limit is not None:
            cmd.extend(["-l", str(limit)])
        if encoder:
            cmd.extend(["-e", encoder])
        if bitrate is not None:
            cmd.extend(["-b", str(bitrate)])
        if rate is not None:
            cmd.extend(["-r", str(rate)])
        if count is not None:
            cmd.extend(["-c", str(count)])
        
        output = self._run_command(cmd)
        if output:
            return self._parse_json_output(output)
        return None

    def microphone_record_info(self) -> Dict:
        """Get information about the current recording."""
        output = self._run_command(["termux-microphone-record", "-i"])
        return self._parse_json_output(output)

    def microphone_record_quit(self) -> None:
        """Stop recording."""
        self._run_command(["termux-microphone-record", "-q"])

    def nfc_read(self, read_type: str = "full") -> Dict:
        """
        Read data from an NFC tag.
        
        Args:
            read_type: Type of read ('short', 'full')
        """
        output = self._run_command(["termux-nfc", "-r", read_type])
        return self._parse_json_output(output)

    def nfc_write(self, text: str) -> None:
        """
        Write data to an NFC tag.
        
        Args:
            text: Text to write
        """
        self._run_command(["termux-nfc", "-w", "-t", text])

    def notification(self, content: str = None, title: str = None, **kwargs) -> None:
        """
        Display a system notification. Content text is specified using content parameter or read from stdin.
        
        Args:
            content: Content to show in the notification (takes precedence over stdin)
            title: Title of the notification
            **kwargs: Additional arguments for the notification, including:
                action: Action to execute when pressing the notification
                alert_once: Do not alert when the notification is edited
                button1: Text to show on the first notification button
                button1_action: Action to execute on the first notification button
                button2: Text to show on the second notification button
                button2_action: Action to execute on the second notification button
                button3: Text to show on the third notification button
                button3_action: Action to execute on the third notification button
                channel: Notification channel id this notification should be sent on
                group: Notification group (notifications with the same group are shown together)
                id: Notification id (will overwrite any previous notification with the same id)
                icon: Icon that shows up in the status bar (default: event_note)
                image_path: Absolute path to an image which will be shown in the notification
                led_color: Color of the blinking led as RRGGBB (default: none)
                led_off: Number of milliseconds for the LED to be off while it's flashing (default: 800)
                led_on: Number of milliseconds for the LED to be on while it's flashing (default: 800)
                on_delete: Action to execute when the notification is cleared
                ongoing: Pin the notification
                priority: Notification priority (high/low/max/min/default)
                sound: Play a sound with the notification
                vibrate: Vibrate pattern, comma separated as in 500,1000,200
                type: Notification style to use (default/media)
                media_next: Action to execute on the media-next button (with type="media")
                media_pause: Action to execute on the media-pause button (with type="media")
                media_play: Action to execute on the media-play button (with type="media")
                media_previous: Action to execute on the media-previous button (with type="media")
                
        Note:
            For action arguments (--action, --on-delete, --button1-action, etc.):
            - Actions are fed to `dash -c`
            - Use actions that do things outside the terminal, like "termux-toast hello"
            - Redirect output if needed: "ls > ~/ls.txt" or "ls|termux-toast"
            - Run multiple commands with: "command1; command2; command3"
            - For complex actions, put your script in a file and use that as the action
            - On Android N or above, use $REPLY for Android's Direct Reply feature
        """
        cmd = ["termux-notification"]
        if title:
            cmd.extend(["-t", title])
        
        for key, value in kwargs.items():
            cmd.extend([f"--{key.replace('_', '-')}", str(value)])
        
        if content:
            cmd.extend(["-c", content])
            self._run_command(cmd)
        else:
            self._run_command(cmd, input_data="")

    def notification_remove(self, notification_id: str) -> None:
        """
        Remove a notification.
        
        Args:
            notification_id: ID of the notification to remove
        """
        self._run_command(["termux-notification-remove", notification_id])

    def notification_list(self) -> List[Dict]:
        """List all notifications."""
        output = self._run_command(["termux-notification-list"])
        return self._parse_json_output(output)

    def notification_channel(self, channel_id: str, channel_name: str = None, delete: bool = False) -> None:
        """
        Create or delete a notification channel.
        
        Args:
            channel_id: ID of the channel
            channel_name: Name of the channel (required for creation)
            delete: Whether to delete the channel
        """
        if delete:
            self._run_command(["termux-notification-channel", "-d", channel_id])
        else:
            if not channel_name:
                raise ValueError("channel_name is required when creating a channel")
            self._run_command(["termux-notification-channel", channel_id, channel_name])

    def open(self, path_or_url: str, send: bool = False, view: bool = True, 
            chooser: bool = False, content_type: str = None) -> None:
        """
        Open a file or URL in an external app.
        
        Args:
            path_or_url: Path or URL to open
            send: Whether to share for sending
            view: Whether to share for viewing
            chooser: Whether to show an app chooser
            content_type: Content type to use
        """
        cmd = ["termux-open"]
        if send:
            cmd.append("--send")
        if not view:
            cmd.append("--no-view")
        if chooser:
            cmd.append("--chooser")
        if content_type:
            cmd.extend(["--content-type", content_type])
        cmd.append(path_or_url)
        self._run_command(cmd)

    def open_url(self, url: str) -> None:
        """
        Open a URL in the default web browser.
        
        Args:
            url: URL to open
        """
        self._run_command(["termux-open-url", url])

    def sensor(self, sensor: str = None, delay: int = None) -> Union[Dict, List[Dict]]:
        """
        Get sensor information.
        
        Args:
            sensor: Specific sensor to query
            delay: Delay between sensor readings in ms
        """
        cmd = ["termux-sensor"]
        if sensor:
            cmd.extend(["-s", sensor])
        if delay is not None:
            cmd.extend(["-d", str(delay)])
        output = self._run_command(cmd)
        return self._parse_json_output(output)

    def share(self, file: str = None, title: str = None, content_type: str = None, action: str = None) -> None:
        """
        Share a file or text.
        
        Args:
            file: File to share
            title: Title for the share dialog
            content_type: Content type of the shared data
            action: Action to perform ('send', 'view')
        """
        cmd = ["termux-share"]
        if title:
            cmd.extend(["-t", title])
        if content_type:
            cmd.extend(["-c", content_type])
        if action:
            cmd.extend(["-a", action])
        if file:
            cmd.extend(["-f", file])
            self._run_command(cmd)
        else:
            self._run_command(cmd, input_data="")

    def sms_list(self, **kwargs) -> List[Dict]:
        """
        List SMS messages.
        
        Args:
            **kwargs: Arguments for filtering SMS messages
        """
        cmd = ["termux-sms-list"]
        for key, value in kwargs.items():
            cmd.extend([f"--{key.replace('_', '-')}", str(value)])
        output = self._run_command(cmd)
        return self._parse_json_output(output)

    def sms_send(self, number: str, message: str = None) -> None:
        """
        Send an SMS.
        
        Args:
            number: Phone number to send to
            message: Message to send
        """
        cmd = ["termux-sms-send", "-n", number]
        if message:
            cmd.extend(["-m", message])
            self._run_command(cmd)
        else:
            self._run_command(cmd, input_data="")

    def speech_to_text(self) -> Dict:
        """Convert speech to text."""
        output = self._run_command(["termux-speech-to-text"])
        return self._parse_json_output(output)

    def storage_get(self, title: str = None) -> str:
        """
        Get a file from shared storage.
        
        Args:
            title: Title for the file picker dialog
        """
        cmd = ["termux-storage-get"]
        if title:
            cmd.extend(["-t", title])
        return self._run_command(cmd)

    def telephony_call(self, number: str) -> None:
        """
        Call a phone number.
        
        Args:
            number: Phone number to call
        """
        self._run_command(["termux-telephony-call", number])

    def telephony_cellinfo(self) -> List[Dict]:
        """Get information about cellular network."""
        output = self._run_command(["termux-telephony-cellinfo"])
        return self._parse_json_output(output)

    def telephony_deviceinfo(self) -> Dict:
        """Get information about the telephony device."""
        output = self._run_command(["termux-telephony-deviceinfo"])
        return self._parse_json_output(output)

    def toast(self, message: str, short: bool = False, position: str = None, 
             background_color: str = None, text_color: str = None) -> None:
        """
        Show a toast message.
        
        Args:
            message: Message to show
            short: Whether to show a short toast
            position: Position of the toast ('top', 'middle', 'bottom')
            background_color: Background color of the toast
            text_color: Text color of the toast
        """
        cmd = ["termux-toast"]
        if short:
            cmd.append("-s")
        if position:
            cmd.extend(["-g", position])
        if background_color:
            cmd.extend(["-b", background_color])
        if text_color:
            cmd.extend(["-c", text_color])
        
        cmd.append(message)
        self._run_command(cmd)

    def torch(self, on: bool = True) -> None:
        """
        Toggle the torch.
        
        Args:
            on: Whether to turn the torch on
        """
        self._run_command(["termux-torch", "on" if on else "off"])

    def tts_engines(self) -> List[Dict]:
        """Get a list of available TTS engines."""
        output = self._run_command(["termux-tts-engines"])
        return self._parse_json_output(output)

    def tts_speak(self, text: str = None, engine: str = None, language: str = None, 
                 region: str = None, variant: str = None, pitch: float = None, 
                 rate: float = None, stream: str = None) -> None:
        """
        Speak text using TTS.
        
        Args:
            text: Text to speak
            engine: TTS engine to use
            language: Language to use
            region: Region to use
            variant: Variant to use
            pitch: Pitch to use
            rate: Rate to use
            stream: Stream to use
        """
        cmd = ["termux-tts-speak"]
        if engine:
            cmd.extend(["-e", engine])
        if language:
            cmd.extend(["-l", language])
        if region:
            cmd.extend(["-n", region])
        if variant:
            cmd.extend(["-v", variant])
        if pitch is not None:
            cmd.extend(["-p", str(pitch)])
        if rate is not None:
            cmd.extend(["-r", str(rate)])
        if stream:
            cmd.extend(["-s", stream])
        
        if text:
            cmd.append(text)
            self._run_command(cmd)
        else:
            self._run_command(cmd, input_data="")

    def usb(self) -> List[Dict]:
        """List USB devices."""
        output = self._run_command(["termux-usb"])
        return self._parse_json_output(output)

    def usb_device(self, device_id: str, callback: str) -> None:
        """
        Listen for USB device events.
        
        Args:
            device_id: ID of the device to listen for
            callback: Command to execute when the device is connected
        """
        self._run_command(["termux-usb", "-r", "-e", callback, device_id])

    def vibrate(self, duration_ms: int = 1000, force: bool = False) -> None:
        """
        Vibrate the device.
        
        Args:
            duration_ms: Duration of vibration in milliseconds
            force: Whether to force vibration
        """
        cmd = ["termux-vibrate"]
        if force:
            cmd.append("-f")
        if duration_ms != 1000:
            cmd.extend(["-d", str(duration_ms)])
        self._run_command(cmd)

    def volume(self, stream: str = None, volume: int = None) -> Union[Dict, List[Dict]]:
        """
        Get or set the volume.
        
        Args:
            stream: Audio stream to set volume for
            volume: Volume level to set
        """
        if stream and volume is not None:
            self._run_command(["termux-volume", stream, str(volume)])
            return None
        else:
            output = self._run_command(["termux-volume"])
            return self._parse_json_output(output)

    def wake_lock(self) -> None:
        """Acquire a wake lock."""
        self._run_command(["termux-wake-lock"])

    def wake_unlock(self) -> None:
        """Release the wake lock."""
        self._run_command(["termux-wake-unlock"])

    def wallpaper(self, file: str, lockscreen: bool = False) -> None:
        """
        Set the wallpaper.
        
        Args:
            file: Image file to use as wallpaper
            lockscreen: Whether to set the lockscreen wallpaper
        """
        cmd = ["termux-wallpaper"]
        if lockscreen:
            cmd.append("-l")
        cmd.extend(["-f", file])
        self._run_command(cmd)

    def wifi_connectioninfo(self) -> Dict:
        """Get information about the current WiFi connection."""
        output = self._run_command(["termux-wifi-connectioninfo"])
        return self._parse_json_output(output)

    def wifi_enable(self, enable: bool = True) -> None:
        """
        Enable or disable WiFi.
        
        Args:
            enable: Whether to enable WiFi
        """
        self._run_command(["termux-wifi-enable", "true" if enable else "false"])

    def wifi_scaninfo(self) -> List[Dict]:
        """Get information about available WiFi networks."""
        output = self._run_command(["termux-wifi-scaninfo"])
        return self._parse_json_output(output)

    def setup_storage(self) -> None:
        """Set up storage permissions and symlinks."""
        self._run_command(["termux-setup-storage"])

    def reload_settings(self) -> None:
        """Reload Termux settings."""
        self._run_command(["termux-reload-settings"])

    def info(self, no_clipboard: bool = False) -> str:
        """
        Get information about Termux and the system.
        
        Args:
            no_clipboard: Whether to not copy the info to the clipboard
        """
        cmd = ["termux-info"]
        if no_clipboard:
            cmd.append("--no-set-clipboard")
        return self._run_command(cmd)

    def job_scheduler(self, **kwargs) -> Union[str, None]:
        """
        Schedule a script to run at specified intervals.
        
        Args:
            **kwargs: Arguments for the job scheduler
        """
        cmd = ["termux-job-scheduler"]
        for key, value in kwargs.items():
            cmd.extend([f"--{key.replace('_', '-')}", str(value)])
        output = self._run_command(cmd)
        if output:
            return output
        return None

    def keystore(self, command: str, *args) -> str:
        """
        Manage keys in the hardware keystore.
        
        Args:
            command: Command to execute ('list', 'delete', 'generate', 'sign', 'verify')
            *args: Additional arguments for the command
        """
        cmd = ["termux-keystore", command]
        cmd.extend(args)
        return self._run_command(cmd)

    def am(self, *args) -> str:
        """
        Execute an Android activity manager command.
        
        Args:
            *args: Arguments for the am command
        """
        cmd = ["termux-am"]
        cmd.extend(args)
        return self._run_command(cmd)

    def change_repo(self) -> None:
        """Change the package repository."""
        self._run_command(["termux-change-repo"])

    def backup(self, output_file: str = None, force: bool = False, 
              ignore_read_failure: bool = False) -> None:
        """
        Back up Termux installation directory.
        
        Args:
            output_file: File to save the backup to
            force: Whether to force write operations
            ignore_read_failure: Whether to ignore read permission denials
        """
        cmd = ["termux-backup"]
        if force:
            cmd.append("--force")
        if ignore_read_failure:
            cmd.append("--ignore-read-failure")
        if output_file:
            cmd.append(output_file)
        self._run_command(cmd)

    def restore(self, input_file: str = None) -> None:
        """
        Restore Termux installation directory from a backup.
        
        Args:
            input_file: File to restore from
        """
        cmd = ["termux-restore"]
        if input_file:
            cmd.append(input_file)
        self._run_command(cmd)

    def fix_shebang(self, file: str) -> None:
        """
        Fix the shebang line in a script.
        
        Args:
            file: File to fix
        """
        self._run_command(["termux-fix-shebang", file])

    def chroot(self, command: str = None) -> str:
        """
        Run a command in a chroot.
        
        Args:
            command: Command to run
        """
        cmd = ["termux-chroot"]
        if command:
            cmd.append(command)
        return self._run_command(cmd)

    def elf_cleaner(self, *files, api_level: int = None, jobs: int = None, 
                   dry_run: bool = False, quiet: bool = False) -> str:
        """
        Clean ELF files.
        
        Args:
            *files: Files to clean
            api_level: Target API level
            jobs: Number of parallel jobs
            dry_run: Whether to only print info without removing entries
            quiet: Whether to not print info about removed entries
        """
        cmd = ["termux-elf-cleaner"]
        if api_level is not None:
            cmd.extend(["--api-level", str(api_level)])
        if jobs is not None:
            cmd.extend(["--jobs", str(jobs)])
        if dry_run:
            cmd.append("--dry-run")
        if quiet:
            cmd.append("--quiet")
        cmd.extend(files)
        return self._run_command(cmd)

    # SAF (Storage Access Framework) methods
    def saf_ls(self, directory_uri: str) -> List[Dict]:
        """
        List files in a SAF directory.
        
        Args:
            directory_uri: URI of the directory
        """
        output = self._run_command(["termux-saf-ls", directory_uri])
        return self._parse_json_output(output)

    def saf_read(self, file_uri: str) -> str:
        """
        Read a file using SAF.
        
        Args:
            file_uri: URI of the file
        """
        return self._run_command(["termux-saf-read", file_uri])

    def saf_write(self, file_uri: str, content: str = None) -> None:
        """
        Write to a file using SAF.
        
        Args:
            file_uri: URI of the file
            content: Content to write
        """
        if content:
            self._run_command(["termux-saf-write", file_uri], input_data=content)
        else:
            self._run_command(["termux-saf-write", file_uri], input_data="")

    def saf_mkdir(self, directory_uri: str, directory_name: str) -> str:
        """
        Create a directory using SAF.
        
        Args:
            directory_uri: URI of the parent directory
            directory_name: Name of the directory to create
        """
        return self._run_command(["termux-saf-mkdir", directory_uri, directory_name])

    def saf_rm(self, file_uri: str) -> None:
        """
        Remove a file using SAF.
        
        Args:
            file_uri: URI of the file
        """
        self._run_command(["termux-saf-rm", file_uri])

    def saf_stat(self, file_uri: str) -> Dict:
        """
        Get information about a file using SAF.
        
        Args:
            file_uri: URI of the file
        """
        output = self._run_command(["termux-saf-stat", file_uri])
        return self._parse_json_output(output)

    def saf_create(self, directory_uri: str, file_name: str, mime_type: str = None) -> str:
        """
        Create a file using SAF.
        
        Args:
            directory_uri: URI of the parent directory
            file_name: Name of the file to create
            mime_type: MIME type of the file
        """
        cmd = ["termux-saf-create", directory_uri, file_name]
        if mime_type:
            cmd.append(mime_type)
        return self._run_command(cmd)

    def saf_dirs(self) -> List[Dict]:
        """Get a list of SAF directories."""
        output = self._run_command(["termux-saf-dirs"])
        return self._parse_json_output(output)

    def saf_managedir(self, directory_uri: str = None) -> Union[str, List[Dict]]:
        """
        Manage SAF directories.
        
        Args:
            directory_uri: URI of the directory to manage
        """
        cmd = ["termux-saf-managedir"]
        if directory_uri:
            cmd.append(directory_uri)
        output = self._run_command(cmd)
        try:
            return self._parse_json_output(output)
        except:
            return output


# Example usage
if __name__ == "__main__":
    termux = TermuxAPI()
    
    # Example: Show a toast
    termux.toast("Hello from Python!")
    
    # Example: Get battery status
    try:
        battery = termux.battery_status()
        print(f"Battery level: {battery['percentage']}%")
    except Exception as e:
        print(f"Error getting battery status: {e}")