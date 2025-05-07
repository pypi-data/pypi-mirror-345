from pynq import DefaultHierarchy, DefaultIP, allocate
import numpy as np
import struct
import time
import requests
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


class AxiStreamHandler():

    def __init__(self, overlay, model_specs):
        self.firmware_name = overlay
        self.supported_boards = {
            'zynq': ['zedboard', 'ebaz4205'],
            'alveo': ['u50']
        }
        self.model_specs = model_specs
        self.batch_size = self.model_specs["batch_size"]
        self.overlay = overlay
        self.fill = False
        self.batches = []
        self.last_batch_size = 0
        self.n_input = self.model_specs['n_input']
        self.n_output = self.model_specs['n_output']
        self.benchcore = self.model_specs['benchcore']
        if self.benchcore == True:
            self.n_output = self.n_output + 1
        self.input_shape  = (self.batch_size, self.n_input)
        self.output_shape = (self.batch_size, self.n_output)
        self.datatype = None
        self.scale = None
        self.__initialize_datatype()
        if self.model_specs['board'] in self.supported_boards['zynq']:
            self.__init_channels()
        if self.model_specs["data_type"][:3] == "fps":
            self.__initialize_fixedpoint()

        self._use_local_flp = self.model_specs["data_type"].startswith("flp")
        if self._use_local_flp:
            self._flp_pool = ThreadPoolExecutor(max_workers=256)
        
    def __bin_to_float16(self, binary_str):
        binary_bytes = int(binary_str, 2).to_bytes(2, byteorder='big')
        float_val = struct.unpack('>e', binary_bytes)[0]
        return float_val

    def __bin_to_float32(self, binary_str):
        byte_str = int(binary_str, 2).to_bytes(4, byteorder='big')
        float_value = struct.unpack('>f', byte_str)[0]
        return float_value

    def __random_pad(self, vec, pad_width, *_, **__):
        vec[:pad_width[0]] = np.random.uniform(0, 1, size=pad_width[0])
        vec[vec.size-pad_width[1]:] = np.random.uniform(0,1, size=pad_width[1])

    def __cast_float_to_binary_to_unsigned(self, num, remote=False):

        exponent_bits = int(self.model_specs["data_type"][4:5])
        mantissa_bits = int(self.model_specs["data_type"][6:len(self.model_specs["data_type"])])
        
        if remote == False:
            try:
                result = subprocess.check_output(['fp2bin', str(exponent_bits), str(mantissa_bits), str(num)],stderr=subprocess.DEVNULL)
                bin_str = result.strip().decode()       # e.g. '010101...'
                return int(bin_str, 2)
            except subprocess.CalledProcessError as e:
                print("Error in subprocess: ", e)
                return 0
        else:
            try:
                

                conversion_url ='http://127.0.0.1:80/bmnumbers'

                strNum = "0flp<"+str(exponent_bits)+"."+str(mantissa_bits)+">"+str(num)
                    
                reqBody = {'action': 'cast', 'numbers': [strNum], 'reqType': 'bin', 'viewMode': 'native'}
                xReq = requests.post(conversion_url, json = reqBody)
                convertedNumber = json.loads(xReq.text)["numbers"][0]
                
                strNumber = convertedNumber[0]+convertedNumber[convertedNumber.rindex(">")+1:len(convertedNumber)]        
                    
                reqBody = {'action': 'show', 'numbers': ["0b"+strNumber], 'reqType': 'unsigned', 'viewMode': 'unsigned'}
                xReq = requests.post(conversion_url, json = reqBody)
                convertedNumber = json.loads(xReq.text)["numbers"][0]

            except Exception as e:
                return 0
        
        return int(convertedNumber)

    def __cast_unsigned_to_bin(self, num, remote=False):

        exponent_bits = int(self.model_specs["data_type"][4:5])
        mantissa_bits = int(self.model_specs["data_type"][6:len(self.model_specs["data_type"])])
        tot_bit_len = exponent_bits + mantissa_bits + 3

        if remote == False:
            binary_string = format(num, '032b')  # 32 bits, zero-padded
            return binary_string[-tot_bit_len:]
        else:
            conversion_url ='http://127.0.0.1:80/bmnumbers'

            reqBody = {'action': 'show', 'numbers': [str(num)], 'reqType': 'bin', 'viewMode': 'bin'}
            xReq = requests.post(conversion_url, json = reqBody)
            convertedNumber = json.loads(xReq.text)["numbers"][0]
        
        return "0"+convertedNumber

    def __convert_binary_to_float(self, num, remote=False):
        
        try:
            exponent_bits = int(self.model_specs["data_type"][4:5])
            mantissa_bits = int(self.model_specs["data_type"][6:len(self.model_specs["data_type"])])

            if remote == False:
                cmd = "bin2fp "+str(exponent_bits)+" "+str(mantissa_bits)+" "+str(num)
                xReq = os.popen(cmd)
                convertedNumber = xReq.read().replace("\n","")
                return float(convertedNumber)
            else:
                conversion_url ='http://127.0.0.1:80/bmnumbers'

                tot_bit_len = exponent_bits + mantissa_bits + 3
                
                strNum = "0b<"+str(tot_bit_len)+">"+str(num)
                
                newType = "flpe"+str(exponent_bits)+"f"+str(mantissa_bits)
                
                reqBody = {'action': 'cast', 'numbers': [strNum], 'reqType': newType, 'viewMode': 'native'}
                xReq = requests.post(conversion_url, json = reqBody)
                
                convertedNumber = json.loads(xReq.text)["numbers"][0]
                strNumber = convertedNumber[convertedNumber.rindex(">")+1:len(convertedNumber)]
                return float(strNumber)
        except Exception as e:
            print(e)
            return float(0)


    def prepare_data(self):
        self.samples_len = len(self.X_test)
        self.fill = False
        self.batches = []

        _, hw_dtype = self.__get_dtype()

        def cast_batch(batch):
            flat = batch.ravel()
            if self.model_specs["data_type"].startswith("fps"):
                # fixed‑point path unchanged
                conv = [self.__float_to_fixed(x) for x in flat]

            elif self._use_local_flp:
                # use threads instead of processes
                futures = [self._flp_pool.submit(self.__cast_float_to_binary_to_unsigned, x)
                           for x in flat]
                # collect in order
                conv = [f.result() for f in futures]

            else:
                return batch.astype(self.__get_dtype()[0])

            arr = np.array(conv, dtype=self.__get_dtype()[1]).reshape(batch.shape)
            return arr

        if self.samples_len <= self.batch_size:
            pad_n = self.batch_size - self.samples_len
            noise = np.random.rand(pad_n, self.X_test.shape[1])
            full = np.vstack([self.X_test, noise])
            self.batches.append(cast_batch(full))

        else:
            n_full = self.samples_len // self.batch_size
            rem    = self.samples_len % self.batch_size

            # full batches
            for i in range(n_full):
                batch = self.X_test[i*self.batch_size:(i+1)*self.batch_size]
                self.batches.append(cast_batch(batch))

            # leftover
            if rem:
                self.fill = True
                self.last_batch_size = rem
                last = self.X_test[n_full*self.batch_size:]
                pad_n = self.batch_size - rem
                noise = np.random.rand(pad_n, self.X_test.shape[1])
                last_padded = np.vstack([last, noise])
                self.batches.append(cast_batch(last_padded))

        print(f"Prepared {len(self.batches)} batches "
            f"(fill={self.fill}, last_batch_size={self.last_batch_size})")


    def __init_channels(self):
        self.sendchannel = self.overlay.axi_dma_0.sendchannel
        self.recvchannel = self.overlay.axi_dma_0.recvchannel

    def __initialize_fixedpoint(self):
        self.total_bits = self.model_specs['register_size']  # Total number of bits
        fractional_bits = int(self.model_specs['data_type'][6:len(self.model_specs['data_type'])])  # Number of fractional bits
        self.scale = 2 ** fractional_bits

    def __float_to_fixed(self, number):
        return int(number * self.scale)

    def __fixed_to_float(self, fixed_number):
        if fixed_number >= (1 << (self.total_bits - 1)):
            fixed_number -= (1 << self.total_bits)
        return fixed_number / self.scale

    def __initialize_datatype_flopoco(self, flopoco_datatype):

        exponent_bits = int(flopoco_datatype[4:5])
        mantissa_bits = int(flopoco_datatype[6:len(flopoco_datatype)])

        total_bits = exponent_bits + mantissa_bits + 3

        if total_bits <= 8:
            self.total_bits = 8
        elif total_bits > 8 and total_bits <= 16:
            self.total_bits = 16
        elif total_bits > 16 and total_bits < 32:
            self.total_bits = 32
        elif total_bits >= 32:
            self.total_bits = 32

        if self.total_bits == 32:
            return "np.uint32"
        elif self.total_bits == 16:
            return "np.uint16"
        elif self.total_bits == 8:
            return "np.uint8"

        
    def __initialize_datatype(self):
        if (self.model_specs["data_type"] == "float16"):
            self.datatype = "np.float16"
        elif (self.model_specs["data_type"] == "float32"):
            self.datatype = "np.float32"
        elif (self.model_specs["data_type"] == "fps16f6"):
            self.datatype = "np.fps16f6"
        elif (self.model_specs["data_type"] == "fps32f16"):
            self.datatype = "np.fps32f16"
        elif (self.model_specs["data_type"].startswith("flpe")):
            print("Data type is flopoco since it starts with flpe")
            self.datatype = self.__initialize_datatype_flopoco(self.model_specs["data_type"])
        else:
            raise Exception("Data type not supported yet")

    def __get_dtype(self):
        if (self.model_specs["data_type"] == "float16"):
            return np.float16, np.uint16
        elif (self.model_specs["data_type"] == "float32"):
            return np.float32, np.uint32
        elif (self.model_specs["data_type"] == "fps16f6"):
            return np.int16, np.int16
        elif (self.model_specs["data_type"] == "fps32f16"):
            return np.int32, np.int32
        elif (self.model_specs["data_type"].startswith("flpe")):
            if self.datatype == "np.uint8" or self.datatype == "np.uint16":
                return np.uint16, np.uint16
            #elif self.datatype == "np.uint16":
            #    return np.uint16, np.uint16
            elif self.datatype == "np.uint32":
                return np.uint32, np.uint32
        else:
            raise Exception("Data type not supported yet")

    def __parse_prediction(self, outputs):
        # Stack all batches into one big (N, n_output) array
        stacked = np.vstack(outputs).astype(int)
        total_samples, n_out = stacked.shape

        # If benchcore, last column is clock cycles
        if self.benchcore:
            clock_cycles = stacked[:, -1].tolist()
            data = stacked[:, :-1]
        else:
            clock_cycles = []
            data = stacked

        # FPS branch: fixed‑point → float by scaling
        if self.model_specs["data_type"].startswith("fps"):
            # data is int array of shape (N, n_output)
            # fixed_to_float is just dividing by scale
            #probs = data.astype(np.float64) / self.scale
            #preds = np.argmax(probs, axis=1).astype(int).tolist()
            hw_classifications = []
            for outcome in outputs:
                for out in outcome:
                    probs = []
                    if self.model_specs["data_type"][:3] == "fps":
                        for i in range(0, self.n_output):
                            if self.benchcore == True and i == self.n_output - 1:
                                clock_cycles.append(out[i])
                            else:
                                prob = self.__fixed_to_float(out[i])
                                probs.append(prob)

                    classification = np.argmax(probs)
                    hw_classifications.append(int(classification))
            
            preds = hw_classifications

        # FLP branch: floating‑point with custom exponent/mantissa
        elif self.model_specs["data_type"].startswith("flp"):
            # convert one row of unsigned ints → float probs + argmax
            def parse_row(row):
                # row is 1‑D array of ints
                # for each element, cast to binary then to float
                floats = [
                    self.__convert_binary_to_float(
                        self.__cast_unsigned_to_bin(int(val)),
                        remote=False
                    )
                    for val in row
                ]
                return int(np.argmax(floats))

            # parallelize across rows with threads
            with ThreadPoolExecutor(max_workers=256) as pool:
                preds = list(pool.map(parse_row, data))

        # IEEE float16 / float32 branch: reinterpret bits as real floats
        else:
            hw_classifications = []
            clock_cycles = []
            for outcome in outputs:
                for out in outcome:
                    probs = []
                    if self.model_specs['register_size'] == 16:
                        for i in range(0, self.n_output):
                            if self.benchcore == True and i == self.n_output - 1:
                                clock_cycles.append(out[i])
                            else:
                                binary_str = bin(out[i])[2:]
                                prob_float = self.__bin_to_float16(binary_str)
                                probs.append(prob_float)

                    elif self.model_specs['register_size'] == 32:
                        for i in range(0, self.n_output):
                            if self.benchcore == True and i == self.n_output - 1:
                                clock_cycles.append(out[i])
                            else:
                                binary_str = bin(out[i])[2:].zfill(32)
                                prob_float = self.__bin_to_float32(binary_str)
                                probs.append(prob_float)
            
                    classification = np.argmax(probs)
                    hw_classifications.append(int(classification))
            
            preds = hw_classifications

        return {'predictions': preds, 'clock_cycles': clock_cycles}
    def release(self):
        self.overlay.free()
        if getattr(self, "_flp_pool", None):
            self._flp_pool.shutdown()

    def predict(self, debug=False):

        latencies = []

        if self.model_specs['board'] in self.supported_boards['zynq']:
            outputs = []
            data_type_input, data_type_output = self.__get_dtype()

            input_buffer = allocate(shape=self.input_shape, dtype=data_type_input)

            for i in range(0, len(self.batches)):
                input_buffer[:]=self.batches[i]
                #print("input buffer: ", input_buffer)
                output_buffer = allocate(shape=self.output_shape, dtype=data_type_output)
                if debug:
                    start_time = time.time()
                #print("Before transfer")
                self.sendchannel.transfer(input_buffer)
                self.recvchannel.transfer(output_buffer)
                self.sendchannel.wait()
                self.recvchannel.wait()
                #print("After transfer")
                #print("output buffer: ", output_buffer)
                if debug:
                    end_time = time.time()
                    time_diff = (end_time - start_time) * 1000
                    latencies.append(time_diff)
                if len(self.batches) == 1:
                    outputs.append(output_buffer)
                else:
                    if self.fill == True and i == len(self.batches) - 1:
                        outputs.append(output_buffer[0:self.last_batch_size])
                    else:
                        outputs.append(output_buffer)

            if debug:
                print("Time taken to predict a batch of size ", self.batch_size, " is ", np.mean(latencies), " ms")
                print("Time taken to predict a single sample is ", np.mean(latencies)/self.batch_size, " ms")
        else:
            outputs = []
            data_type_input, data_type_output = self.__get_dtype()

            bm_krnl = self.overlay.krnl_bondmachine_rtl_1

            input_buffer = allocate(shape=self.input_shape, dtype=data_type_input)

            for i in range(0, len(self.batches)):
                input_buffer[:]=self.batches[i]
                output_buffer = allocate(shape=self.output_shape, dtype=data_type_output)
                input_buffer.sync_to_device()
                if debug:
                    start_time = time.time()
                bm_krnl.call(input_buffer, output_buffer)
                output_buffer.sync_from_device()
                if debug:
                    end_time = time.time()
                    time_diff = (end_time - start_time) * 1000
                    latencies.append(time_diff)

                if len(self.batches) == 1:
                    outputs.append(output_buffer)
                else:
                    if self.fill == True and i == len(self.batches) - 1:
                        outputs.append(output_buffer[0:self.last_batch_size])
                    else:
                        outputs.append(output_buffer)

            #print(outputs)
            if debug:
                print("Time taken to predict a batch of size ", self.batch_size, " is ", np.mean(latencies), " ms")
                print("Time taken to predict a single sample is ", np.mean(latencies)/self.batch_size, " ms")
                print("Standard deviation of the time taken to predict a batch of size ", self.batch_size, " is ", np.std(latencies), " ms")
                print("Standard deviation of the time taken to predict a single sample is ", np.std(latencies)/self.batch_size, " ms")
                
        result = self.__parse_prediction(outputs)

        del input_buffer
        del output_buffer

        return result
            




