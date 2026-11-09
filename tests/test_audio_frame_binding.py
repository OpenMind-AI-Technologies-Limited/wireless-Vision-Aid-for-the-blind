"""Frame-id association at TTS queue boundary; no physical speaker test."""
import queue

from core.udp_runtime import UDPVisionServer


def test_speech_queue_preserves_frame_capture_context():
    server = UDPVisionServer.__new__(UDPVisionServer)
    server.enable_tts = True
    server.speech_queue = queue.Queue(maxsize=1)
    server._current_capture_context = (111, 27, 989001)
    server._speak("chair on left")
    message, created_mono, context = server.speech_queue.get_nowait()
    assert message == "chair on left"
    assert created_mono > 0
    assert context == (111, 27, 989001)


def test_speech_queue_discards_oldest_when_full():
    server = UDPVisionServer.__new__(UDPVisionServer)
    server.enable_tts = True
    server.speech_queue = queue.Queue(maxsize=1)
    server._current_capture_context = (111, 2, 120)
    server._speak("previous obstacle")
    server._current_capture_context = (111, 3, 200)
    server._speak("more urgent obstacle")
    message, _, context = server.speech_queue.get_nowait()
    assert message == "more urgent obstacle"
    assert context[1] == 3
