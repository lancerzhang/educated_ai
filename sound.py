# 1 second = 86.5 mel frames
# find max energy position
# expend the width to 3, add tolerance
# detect if it elapse more than 3 frames, if yes, save to memory
# next time, can detect if has such activation
# if recall many times, can explore more features

import librosa, math, audioop, time, pyaudio, collections, util, memory
import librosa.display as dsp
import numpy as np

start_thread = True
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
SAMPLE_WIDTH = 2  # 16-bit
ENERGY_THRESHOLD = 1500  # minimum audio energy to consider for recording
BUFFER_THRESHOLD = 0.5  # second of buffer

MEL_NUMBER = 128
MFCC_NUMBER = 13

phases = collections.deque()  # phases queue
MAX_PHASES = 5  # max phases storage
REST_SECONDS = 0.01  # take some rest if too many phases are not handled
FRAME_SECOND = 0.1  # process phase per frame, each frame is 0.1 seconds

db = None
FEATURE = 'ftr'
INDEX = 'nps'
ENERGY = 'ngy'
FEATURE_MAX_ENERGY = 1
FEATURE_MFCC = 2
SIMILARITY = 0.1
MFCC_GAP_THRESHOLD = 0.03
last_mfcc = None


def listen():
    print 'start to listen.\n'
    try:
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=SAMPLE_RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
        while start_thread:

            # take some rest if too many phases are not handled
            if len(phases) > MAX_PHASES:
                time.sleep(REST_SECONDS)
                break

            frame_count = 0
            frame_data = []
            seconds_per_buffer = float(CHUNK) / SAMPLE_RATE
            buffer_count = int(math.ceil(BUFFER_THRESHOLD / seconds_per_buffer))

            # do nothing until frame energy reach threshold
            while True:
                buffer = stream.read(CHUNK)
                if len(buffer) == 0: break  # reached end of the stream
                # detect whether speaking has started on audio input
                energy = audioop.rms(buffer, SAMPLE_WIDTH)  # energy of the audio signal
                if energy > ENERGY_THRESHOLD:
                    # save the frame
                    np_buffer = np.fromstring(buffer, dtype=np.int16)
                    normal_buffer = util.normalizeAudioData(np_buffer)
                    frame_data.append(normal_buffer)
                    frame_count += 1
                    break

            # start to record
            while True:
                buffer = stream.read(CHUNK)
                if len(buffer) == 0: break  # reached end of the stream
                energy = audioop.rms(buffer, SAMPLE_WIDTH)  # energy of the audio signal
                np_buffer = np.fromstring(buffer, dtype=np.int16)
                normal_buffer = util.normalizeAudioData(np_buffer)
                frame_data.append(normal_buffer)
                frame_count += 1
                if frame_count >= buffer_count or energy < ENERGY_THRESHOLD:
                    break

            # reach buffer threshold, start to process
            npArr = np.array(frame_data)
            y = npArr.flatten()
            phases.append(y)

    except KeyboardInterrupt:
        pass
    except:
        pass


def mix_energy(energy, memories):
    for mem in memories:
        db.update_memory_ids({ENERGY: (energy + mem[ENERGY]) / 2}, [mem.doc_id])


# given 2 mfcc arrays, find out shift, look up them in memories
def process_frame_mfcc_feature(frame_working_memories, current_data, last_data):
    mfcc_gaps = current_data - last_data
    mfcc_gaps_abs = abs(mfcc_gaps)
    max_index = np.argmax(mfcc_gaps_abs)
    max_index = max_index.astype(np.int32)
    sim_result = util.calculate_similarity(current_data[max_index], SIMILARITY)
    features = db.use_sound2(FEATURE_MFCC, max_index, ENERGY, sim_result[0], sim_result[1])
    if len(features) == 0:
        # if no, add one to memory
        mem = db.add_sound({FEATURE: FEATURE_MFCC, INDEX: max_index, ENERGY: current_data[0]})
        frame_working_memories.append(mem)
    else:
        mix_energy(current_data[max_index], features)
        frame_working_memories += features


def impress(working_memory_sound):
    if len(phases) == 0:
        return
    phase = phases.popleft()
    # process phase per frame
    frames = []
    phase_seconds = float(phase.size) / SAMPLE_RATE
    number_of_frames = int(phase_seconds / FRAME_SECOND)
    if number_of_frames <= 1:
        frames.append(phase)
    else:
        frames = np.array_split(phase, number_of_frames)
    # start to process frames
    for frame in frames:
        mfccs = librosa.feature.mfcc(frame, sr=SAMPLE_RATE, n_mfcc=MFCC_NUMBER)
        mfcc_data = np.average(mfccs, axis=1)
        global last_mfcc
        if last_mfcc is None:
            last_mfcc = mfcc_data
            continue
        frame_working_memories = []
        process_frame_mfcc_feature(frame_working_memories, mfcc_data, last_mfcc)

        # see if we have such feature in memory
        # features2 = db.use_sound(FEATURE_MFCC, ENERGY, max_energy * (1 - SIMILARITY), max_index * (1 - max_energy))
        # if len(features2) == 0:
        #     # if no, add one to memory
        #     mem = db.add_sound({FEATURE: FEATURE_MFCC, ENERGY: max_energy})
        #     frame_working_memories.append(mem)
        # now group the (new or found) feature memories
        # frame_working_memories = features1 + features2
        # frame_working_memories = features1
        # try to find out parent memory, emphasize it
        common_parents = []
        if len(frame_working_memories) > 1:
            common_parents = memory.find_common_parents(frame_working_memories)
        # if still have feature memory, group them all to a new parent memory
        temp_memories = frame_working_memories + common_parents
        if len(temp_memories) > 1:
            db.add_parent(temp_memories)


# get strongest energy and its left&right energy
def get_max_energy(data):
    energy = data.max()
    max_index = np.argmax(data)
    if max_index > 0:
        energy += data[max_index - 1]
    if max_index < len(data) - 1:
        energy += data[max_index + 1]
    return energy
