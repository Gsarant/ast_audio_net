from transformers import AutoFeatureExtractor, ASTForAudioClassification
import torch
import librosa
from datetime import datetime
import sys
sys.path.append('./misc')
from log_test import logger
LOG_D={'module_name':'ast_model'}

def cuda_check():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}",extra=LOG_D)
    

#Additional Info when using cuda
    if device.type == 'cuda':
        logger.info(f"Cuda device {torch.cuda.get_device_name(0)}")
        logger.info('Memory Usage:',extra=LOG_D)
        logger.info(f"Allocated: {round(torch.cuda.memory_allocated(0)/1024**3,1)} GB",extra=LOG_D)
        logger.info(f"Cached:    {round(torch.cuda.memory_reserved(0)/1024**3,1)} GB",extra=LOG_D)
    return device

class AST():

    def __init__(self):
        self.device=cuda_check()
        init_start_inf=datetime.now()
        path_model='ast-finetuned-audioset-10-10-0.4593'
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(path_model,local_files_only=True, device_map =self.device)
        self.model = ASTForAudioClassification.from_pretrained(path_model,local_files_only=True, device_map =self.device)
        self._samplerate_ast=16000
        total_start_inf=datetime.now()
        logger.info(f"Init AST time: {datetime.now()-init_start_inf}",extra=LOG_D)
          
    def inference(self,waveform, sample_rate):
        total_start_inf=datetime.now()

        start_inf=datetime.now()
        logger.info('Start inference',extra=LOG_D)
        if sample_rate !=   self._samplerate_ast:
            waveform= librosa.resample(y=waveform,orig_sr=sample_rate,target_sr=  self._samplerate_ast, res_type="scipy")
            logger.info(f"Resample, time: {datetime.now()-start_inf}",extra=LOG_D)
        start_inf=datetime.now()     
        inputs = self.feature_extractor(waveform, sampling_rate= self._samplerate_ast, return_tensors="pt")
        logger.info(f"Feature extracting time: {datetime.now()-start_inf}",extra=LOG_D)
        start_inf=datetime.now()
        with torch.no_grad():
            logits = self.model(**inputs).logits
        logger.info(f"Inference time: {datetime.now()-start_inf}",extra=LOG_D)  
        logger.info(f"Total Inference time: {datetime.now()-total_start_inf}",extra=LOG_D)  
        return  self.__show_prediction(logits=logits)
    
    def __show_prediction(self,logits):
        if not logits is None:
            predicted_class_ids = torch.argmax(logits, dim=-1).item()
            confs=torch.nn.Softmax()(logits)
            predicted_class_ids = torch.topk(logits,k=4)
            predicted_label_list=[]

            for predicted_class_id in predicted_class_ids[1][0]:
                index=predicted_class_id.detach().cpu().item()
               
                predicted_label_list.append({'sound':self.model.config.id2label[index], 'conf':confs[0][index].detach().cpu().item()}) 
            
        return predicted_label_list

    
    

