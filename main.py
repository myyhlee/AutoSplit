import numpy as np
from glob import glob
from tqdm import tqdm
import os

import argparse

import librosa
import soundfile
import torch
import eappl


def str2bool(v):
    return v.lower() in ("true", "1", "y", "t", "ㅇㅇ")


def main(input_dir: str = "original_audio",
         output_dir: str = "processed",
         file_name: str = "processed",
         sampling_rate: int = 22050,
         save_length: float = 5.0,
         noise_reduction_dtln: bool = False,
         remove_silence: bool = True,
         remove_silence_top_db: int = 35,
         output_trimming: bool = True,
         remove_deviants: bool = False,
         deviant_threshold: int = 0.3,
         required_silence: float = 0.15,
         force_max_length: bool = False):

    if noise_reduction_dtln == True:
        print("Using noise reduction with DTLN")
        denoiser = eappl.Denoise()
    else:
        print("Does not activate noise reduction")

    save_frames = int(sampling_rate * save_length)

    # wav 파일이름 리스트 불러오기
    wav_files = glob(os.path.join("./", input_dir, "*.wav"))
    print(wav_files)

    # 웨이브폼 저장, 트리밍, 사일런스 제거
    concat_wav = np.ndarray([0])

    print("Loading original .wav file")
    for wav_file in tqdm(wav_files):
        y, sr = librosa.load(wav_file, sr=sampling_rate)
        y, _ = librosa.effects.trim(y)
        concat_wav = np.concatenate((concat_wav, y), axis=0)
    print("Loading done")

    if not os.path.exists(os.path.join("./", output_dir)):
        os.makedirs(os.path.join("./", output_dir))

    # 오리지널 웨이브폼 사이 모든 사일런스 제거
    if remove_silence == True:
        print("Removing silence")
        concat_wav = concat_wav.tolist()
        concat_wav = [i for i in concat_wav if i != 0.0]
        concat_wav = np.array(concat_wav)

        clips = librosa.effects.split(concat_wav, top_db=remove_silence_top_db)

        wav_data = []
        for c in tqdm(clips):
            data = concat_wav[c[0]: c[1]]
            wav_data.extend(data)

        concat_wav = np.array(wav_data)

    # 샘플 타임축 카운트
    count = 0
    # 저장되어 .wav로 저장될 배열
    sav = np.ndarray([0, ])
    # 저장되는 .wav 파일의 넘버링
    num = 1
    # 사일런스 카운트 토큰
    s_count = 0

    # 처리후 기준치보다 짧거나, 긴 .wav 파일들 리스트
    short_list = []
    long_list = []

    print("Splitting in progress")
    for i in tqdm(concat_wav):
        count += 1
        i = np.array([i])
        sav = np.concatenate((sav, i), axis=0)

        if count >= save_frames:  # save_length 초 이상의 샘플들이 쌓인 이후엔

            s_count += 1  # 사일런스 카운트를 증가시킴
            if i >= 0.05:  # 목소리로 판별 하이퍼 파라미터: 사일런스가 아닌순간이 오면 판단되면 자르기
                s_count = 0  # 목소리가 인식되면 사일런스 카운트 초기화

                # force_max_length 관한것
                if force_max_length:
                    if len(sav) > save_frames:
                        s_count = int(sampling_rate * required_silence)
                else:
                    pass

        # 사일런스카운트가 n개 쌓이면 사일런스 구간이라고 판단하고 저장
        if s_count == int(sampling_rate * required_silence):

            # 트리밍
            if output_trimming == True:
                sav, _ = librosa.effects.trim(sav, top_db=remove_silence_top_db)

            # DTLN으로 디노이징
            if noise_reduction_dtln == True:
                sav = denoiser(sav, sampling_rate)

            if len(sav) < (save_frames * (1 - deviant_threshold)):
                short_list.append(num)

            if len(sav) > (save_frames * (1 + deviant_threshold)):
                long_list.append(num)

            # 기준치보다 짧거나, 긴 .wav 파일들은 저장하지 않음
            if remove_deviants == True:
                if len(sav) < (save_frames * (1 - deviant_threshold)) or len(sav) > (save_frames * (1 + deviant_threshold)):
                    print(
                        f"audio num: {num} is too short or long, so it is not saved.")

                else:
                    soundfile.write(os.path.join(
                        "./", output_dir, f"{file_name}_{num}.wav"), sav, sampling_rate)
            else:
                soundfile.write(os.path.join("./", output_dir,
                                             f"{file_name}_{num}.wav"), sav, sampling_rate)

            num += 1
            count = 0
            sav = np.ndarray([0])  # 오디오 저장될 배열 초기화
            s_count = 0

    if remove_deviants == True:
        print("Saving is done.")
        print(f"unsaved short audio files: {short_list}")
        print(f"unsaved long audio files: {long_list}")
        if len(short_list) != 0 or len(long_list) != 0:
            print(
                f" {len(short_list) + len(long_list)} out of {num} audio files are not saved.")
        elif len(short_list) == 0 and len(long_list) == 0:
            print("All audio files are saved.")

    else:
        print("Saving is done.")
        print(f"short audio files: {short_list}",
              "\n", "count: ", len(short_list))
        print(f"long audio files: {long_list}",
              "\n", "count: ", len(long_list))
        if len(short_list) != 0 or len(long_list) != 0:
            print(
                f" {len(short_list) + len(long_list)} out of {num} audio files are too short or long.")
        elif len(short_list) == 0 and len(long_list) == 0:
            print("All audio files are saved.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_dir',
                        type=str,
                        default='original_audio',
                        help='input directory')
    parser.add_argument('--output_dir',
                        type=str,
                        default='processed',
                        help='output directory')
    parser.add_argument('--file_name',
                        type=str,
                        default='processed',
                        help='file names for processed .wav files')
    parser.add_argument('--sampling_rate',
                        type=int,
                        default=22050,
                        help='sampling rate')
    parser.add_argument('--save_length',
                        type=float,
                        default=5,
                        help='audio length to be saved(in sec)')
    parser.add_argument('--noise_reduction_dtln',
                        type=str2bool,
                        default=False,
                        help='noise reduction using DTLN')
    parser.add_argument('--remove_silence',
                        type=str2bool,
                        default=True,
                        help='remove silence (zeros) from original audio')
    parser.add_argument('--remove_silence_top_db',
                        type=int,
                        default=35,
                        help='top_db for silence removal')
    parser.add_argument('--output_trimming',
                        type=str2bool,
                        default=True,
                        help='trimming output audio')
    parser.add_argument('--remove_deviants',
                        type=str2bool,
                        default=False,
                        help='remove audio files that are too short or too long')
    parser.add_argument('--deviant_threshold',
                        type=float,
                        default=0.3,
                        help='threshold for audio files that are too short or too long: 0.2 means 20 percent shorter or longer than save_length')
    parser.add_argument('--required_silence',
                        type=float,
                        default=0.15,
                        help='required silence length to save audio(in sec)')
    parser.add_argument('--force_max_length',
                        type=str2bool,
                        default=False,
                        help='force all audio files to have the maximum length of the setted value no matter how each auido file ends')

    args = parser.parse_args()

    print(args)

    if not os.path.exists(os.path.join("./", args.output_dir)):
        os.makedirs(os.path.join("./", args.output_dir))

    f = open(os.path.join("./", args.output_dir, f"{args.file_name}.txt"), 'w')
    d = vars(args)
    for i in d:
        f.write(f"{i}: {d[i]} \n")
    f.write("\n")    
    f.write(f"The following audio source files are used: \n")
    wave_files = glob(os.path.join("./", args.input_dir, "*.wav"))
    for i in wave_files:
        f.write(f"{i} \n")
    f.close()
    
    main(input_dir=args.input_dir,
         output_dir=args.output_dir,
         file_name=args.file_name,
         sampling_rate=args.sampling_rate,
         save_length=args.save_length,
         noise_reduction_dtln=args.noise_reduction_dtln,
         remove_silence=args.remove_silence,
         remove_silence_top_db=args.remove_silence_top_db,
         output_trimming=args.output_trimming,
         remove_deviants=args.remove_deviants,
         deviant_threshold=args.deviant_threshold,
         required_silence=args.required_silence,
         force_max_length=args.force_max_length)
