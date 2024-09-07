import lzma
import lzham
import zstandard


def decompress(data):
    version = 1

    if data[:2] == b'SC':
        # Skip the header if there's any
        pre_version = int.from_bytes(data[2: 6], 'big')

        if pre_version == 4:
            version = int.from_bytes(data[6: 10], 'big')
            hash_length = int.from_bytes(data[10: 14], 'big')
            end_block_size = int.from_bytes(data[-4:], 'big')

            if version == 3:
                # skip the end block size and the 'START' tag
                data = data[14 + hash_length:-end_block_size - 9]

            else:
                # version != 3 does not have a 'START' tag
                data = data[14 + hash_length:-end_block_size - 4]

        else:
            version = pre_version
            hash_length = int.from_bytes(data[6: 10], 'big')
            data = data[10 + hash_length:]

    if version in (1, 3):
        if data[:4] == b'SCLZ':
            dict_size = int.from_bytes(data[4:5], 'big')
            uncompressed_size = int.from_bytes(data[5:9], 'little')
            decompressed = lzham.decompress(
                data[9:], uncompressed_size, {'dict_size_log2': dict_size})

        elif data[:4] == bytes.fromhex('28 B5 2F FD'):
            decompressed = zstandard.decompress(data)

        else:
            data = data[0:9] + (b'\x00' * 4) + data[9:]
            decompressor = lzma.LZMADecompressor()

            output = []

            while decompressor.needs_input:
                output.append(decompressor.decompress(data))

            decompressed = b''.join(output)

    else:
        decompressed = data

    return decompressed
