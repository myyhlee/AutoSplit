# todo
[ ] poetry add librosa 문제 해결

# 설명
여러 .wav파일의 오디오 파일을 모두 이어 붙힌 뒤, 원하는 길이만큼의 오디오 파일로 잘라서 반환해줌.
다만, 자르려고 하는 시점에서 오디오 파일 내 화자가 말을 하고 있다고 판단이 되면, 음성 퀄리티 보존을 위해 
자르기를 보류하고, 가장 먼저 출현하는 silence 구간이 나올때까지 기다렸다가 반환함.

# 사용법:
requirements.txt 설치 (대부분 기본적인 라이브러리이지만 노이즈 제거 기능 사용 원할시 eappl 설치 필요.)

아래 코드 실행

python main.py \
--input_dir original_audio \
--output_dir processed \
--file_name RheeCH \
--sampling_rate 22050 \
--save_length 5.2 \
--noise_reduction_dtln False \
--remove_silence True \
--remove_silence_top_db 40 \
--output_trimming True \
--remove_deviants False \
--deviant_threshold 0.05 \
--required_silence 0.15 \
--force_max_length True


# arguments 설명
python main.py \
--input_dir original_audio \ # 오디오 파일이 저장된 디렉토리: 1개 이상의 .wav 파일들 집어 넣어놓으면 됨.

--output_dir processed \  # 잘린 오디오 파일이 저장 될 디렉토리.

--file_name processed \ # output_dir에 담길 .wav 파일의 이름.

--sampling_rate 22050 \ # 샘플링 레이트.

--save_length 5.0 \ # 자르고자 하는 오디오 길이 (초).

--noise_reduction_dtln False \ # 잘린 오디오 파일 DTLN 이용해서 노이즈 제거할건지.

--remove_silence True \ # 최초에 원본오디오 파일 불러올때 사일런스 제거할지: librosa.effects.split 사용

--remove_silence_top_db \ # remove_silence와 output_trimming 기준 top_db: librosa.effects.split 참조, 디폴트: 40

--output_trimming True \ # 5초간격으로 자른 오디오 파일 양 끝 사일런스를 없앨지 (해당 값 True시 5초 미만으로 줄어들 가능성 높음).

--remove_deviants False \ # output_trimming 이 True 일 시, save_length에서 설정한 기준 길이보다 짧아진 데이터가 생김. 해당 데이터들을 그냥 삭제할지 여부. 또한 오디오의 음성이 5초보다 길게 저장되는 경우도 있음. 이러한 데이터들을 저장하지 않고 그냥 삭제할지 여부.

--deviant_threshold 0.3 \ # remove_deviants 에서 삭제 될 이상 길이를 가진 오디오들의 기준치. 0.3 이면 기준치인 5초의 70퍼센트(3.5초)의 길이를 가진 오디오부터, 130퍼센트의 길이를가진 오디오 (6.5초)까지 정상범위로 판단.

--required_silence \ 0.15 # 5초간격의 샘플이 쌓이고, 그 후 일정 시간 사일런스구간이 연속적으로 등장하면 끊을 수 있는 오디오로 판단함. 따라서, required_silence는 설정한 샘플링 레이트에 대해 몇퍼센트의 길이만큼을 충분한 사일런스 구간으로 설정할지 정함. 0.15의 경우에는 설정된 샘플링 레이트(i.e. 22050)의 15퍼센트인 약 3308 샘플만큼의 사일런스가 연속적으로 출현하면 그 전까지의 오디오를 저장함.

--force_max_length # 오디오의 최대길이를 제한해서, save_length를 넘어가면 무조건 저장 (사일런스 고려하지않고)