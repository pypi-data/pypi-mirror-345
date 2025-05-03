from .compatability_utils import *
from abstract_utilities import get_media_types
from abstract_utilities.json_utils import get_create_json_data
from .file_utils import *
from moviepy.editor import *
import moviepy.editor as mp
from abstract_ocr.ocr_utils import extract_image_texts_from_directory
from .audio_utils import *
from .seo_utils import get_seo_data
from .text_tools import *

def if_none_get_default(obj=None,default=None):
    if obj == None:
        obj = default
    return obj

class VideoTextPipeline:
    def __init__(self, video_path=None, output_dir=None, output_path=None, new_filename=None, info_data=None, output_option=None, info_path=None,whisper_result_path=None, reencode=None, frame_interval=None, remove_phrases=None):
        self.info = {}
        self.remove_phrases = remove_phrases or []
        self.reencode = if_none_get_default(obj=reencode, default=False)
        self.video_path = video_path
        self.info["video_path"] = self.video_path
        self.video_id = generate_file_id(self.video_path)
        self.info["video_id"] = self.video_id
        
        # Set output_path, ensuring it’s unique
        self.output_path = get_path(self.video_path, output_dir=output_dir, output_path=output_path, new_filename=new_filename)
        if self.output_path == self.video_path:
            self.output_path = create_unique_filename(self.video_path)  # Ensure unique output path
        self.output_dir = os.path.dirname(self.output_path)
        self.info["info_dir"] = self.output_dir
        
        # Set output_option, defaulting to "copy" for safety
        self.output_option = output_option or "copy"
        self.info["output_path"] = self.output_path
        
        self.info_path = info_path or os.path.join(self.output_dir, 'info.json')
        self.info["info_path"] = self.info_path
        self.whisper_result_path = whisper_result_path or os.path.join(self.output_dir, 'whisper_result.json')
        self.info["whisper_result_path"] = self.whisper_result_path
        self.thumbnails_directory = os.path.join(self.output_dir, 'thumbnails')
        self.info["thumbnails_directory"] = self.thumbnails_directory  # Fixed typo: was self.info_path
        self.frame_interval = if_none_get_default(obj=frame_interval, default=1)
        self.original_dir = os.path.dirname(self.video_path)
        self.audio_path = os.path.join(self.output_dir, 'audio.wav')
        self.info['audio_path'] = self.audio_path
        self.is_optimized = is_video_optimized(self.video_path)
        self.info_data = self.get_info(info_path=self.info_path,data=self.info)
        self.info_data["is_optimized"] = self.info_data.get("is_optimized") or self.is_optimized
        
    def get_info(self,info_path=None,data=None):
        data = data or {}
        self.info_path = info_path or self.info_path
        if not os.path.isfile(self.info_path):
            safe_dump_to_file(data=data,file_path=self.info_path)
        else:
            og_data = safe_load_from_file(self.info_path)
            og_data.update(data)
            safe_dump_to_file(data=og_data,file_path=self.info_path)
        return safe_load_from_file(self.info_path)
    def needs_conversion(self) -> bool:
        if not self.is_optimized:
            optimize_video_for_safari(
                input_file=self.video_path,
                output_option=self.output_option,
                output_path=self.output_path,
                reencode=self.reencode
            )
        elif os.path.isfile(self.output_path):
            input_hash = compute_file_hash(self.video_path, chunk_size=8192)
            output_hash = compute_file_hash(self.output_path, chunk_size=8192)
            if input_hash == output_hash:
                return
            self.final_output = handle_output_option(self.video_path,self.output_path,self.output_option)
        else:
            self.final_output = handle_output_option(self.video_path,self.output_path,self.output_option)
        self.info_data["is_optimized"] = True
        return self.info_data.get("video_text") is None
    def needs_transcription(self):
        whisper_result={}
        if not os.path.isfile(self.whisper_result_path):
            whisper_result = transcribe_with_whisper_local(audio_path=self.audio_path)
            safe_dump_to_file(data=whisper_result,file_path=self.whisper_result_path)
        whisper_result = get_create_json_data(file_path=self.whisper_result_path,data=whisper_result)
        if whisper_result.get('language'):
            return whisper_result
        if not whisper_result.get('text') or whisper_result.get('segments'):
            whisper_result = transcribe_with_whisper_local(audio_path=self.audio_path)
            safe_dump_to_file(data=whisper_result,file_path=self.whisper_result_path)
        return whisper_result
    def needs_text(self,whisper_text = None):
        info_data = self.info_data
        whisper_text or get_whisper_text_data(info_data=info_data)
        summary = info_data.get('summary')
        description = info_data.get('description')
        keywords = info_data.get('keywords')
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        if description == None:
            info_data['description'] = summarizer(whisper_text[:1000], max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        if keywords == None:
            info_data = refine_keywords(full_text=whisper_text, top_n=5,info_data=info_data)
        if summary == None:
            info_data['summmary'] = get_summary(full_text=whisper_text, max_words=200, max_length=100, min_length=50)
        self.info_data = info_data
        return self.info_data
        
    def extract_frames(self):
        video_path = self.video_path
        directory  = self.thumbnails_directory
        interval   = self.frame_interval
        vid_id     = self.video_id

        clip = VideoFileClip(video_path)
        duration = int(clip.duration)

        os.makedirs(directory, exist_ok=True)
        for t in range(0, duration, interval):
            frame_file = os.path.join(directory, f"{vid_id}_frame_{t}.jpg")
            if not os.path.isfile(frame_file):
                frame = clip.get_frame(t)
                # cv2 import assumed in your routes.py
                import cv2, numpy as np
                cv2.imwrite(frame_file, cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))

    def ocr_images(self, existing_texts=None):
        return extract_image_texts_from_directory(
            directory=self.thumbnails_directory,
            image_texts=existing_texts or [],
            remove_phrases=self.remove_phrases)
        
        
    def run(self):
        """Perform the full OCR pipeline and update info_data & JSON on disk."""
        self.needs_conversion()
        extract_audio_from_video(video_path=self.output_path, audio_path=self.audio_path)
        # 1) extract frames
        self.extract_frames()
        
        # 2) OCR-the-frames
        texts = self.ocr_images(existing_texts=self.info_data.get("video_text"))
        self.info_data["video_text"] = texts
        whisper_result = self.needs_transcription()
        # 3) persist to your JSON store
        #    update_json_data comes from abstract_utilities.json_utils
        self.info_data = self.needs_text(whisper_text = whisper_result.get('text'))
        self.info_data = get_seo_data(info_data = self.info_data,
                                      infos_dir = self.output_dir)
        
        safe_dump_to_file(data=self.info_data,
                          file_path=self.info["info_path"])
        return self.info_data
