import os
import struct
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class GAFOFileEntry:
    filename: str
    offset: int
    size: int
    compressed_size: int
    is_compressed: bool

class GAFOFILE:
    def __init__(self, compression_level: int = 6):
        """
        Initialize GAFOFILE compressor with compression level (1-9)
        """
        self.compression_level = max(1, min(9, compression_level))
        self.window_size = 2 ** (12 + self.compression_level // 3)
        self.lookahead_buffer = 2 ** (4 + self.compression_level // 3)

    def _lz77_compress(self, data: bytes) -> bytes:
        """LZ77 compression with adaptive window size"""
        compressed = bytearray()
        pos = 0
        len_data = len(data)
        
        while pos < len_data:
            best_offset, best_length = 0, 0
            window_start = max(0, pos - self.window_size)
            
            # Search for the longest match
            for candidate in range(window_start, pos):
                length = 0
                while (pos + length < len_data and 
                       candidate + length < pos and
                       data[candidate + length] == data[pos + length] and
                       length < self.lookahead_buffer):
                    length += 1
                
                if length > best_length:
                    best_length = length
                    best_offset = pos - candidate
            
            if best_length >= 3:  # Minimum match length
                # Encode as (offset, length) pair (GAFO format)
                compressed.extend(self._encode_token(best_offset, best_length))
                pos += best_length
            else:
                # Encode as literal
                compressed.append(0x80)  # Literal marker
                compressed.append(data[pos])
                pos += 1
        
        return bytes(compressed)

    def _encode_token(self, offset: int, length: int) -> bytearray:
        """GAFO token encoding (12-bit offset, 6-bit length)"""
        token = bytearray()
        token.append((offset >> 4) & 0xFF)
        token.append(((offset & 0x0F) << 4) | ((length - 3) & 0x3F))
        return token

    def _adaptive_huffman_encode(self, data: bytes) -> bytes:
        """Two-level adaptive Huffman encoding"""
        # First level: Simple frequency-based Huffman
        freq = defaultdict(int)
        for byte in data:
            freq[byte] += 1
        
        codes = self._build_huffman_codes(freq)
        
        # Second level: Encode with header containing code table
        encoded = bytearray()
        
        # Write header (code table)
        encoded.append(len(freq))  # Number of unique bytes
        
        for byte, count in freq.items():
            encoded.append(byte)
            encoded.extend(struct.pack('>H', count))
        
        # Write encoded data
        bit_buffer = []
        for byte in data:
            bit_buffer.extend(codes[byte])
            
            while len(bit_buffer) >= 8:
                byte_val = 0
                for i in range(8):
                    if bit_buffer[i]:
                        byte_val |= 1 << (7 - i)
                encoded.append(byte_val)
                bit_buffer = bit_buffer[8:]
        
        # Flush remaining bits
        if bit_buffer:
            padding = 8 - len(bit_buffer)
            byte_val = 0
            for i in range(len(bit_buffer)):
                if bit_buffer[i]:
                    byte_val |= 1 << (7 - i)
            encoded.append(byte_val)
            encoded.append(padding)  # Store padding length
        else:
            encoded.append(0)  # No padding
        
        return bytes(encoded)

    def _build_huffman_codes(self, freq: Dict[int, int]) -> Dict[int, List[int]]:
        """Build Huffman codes from frequency table"""
        heap = [[weight, [byte, ""]] for byte, weight in freq.items()]
        heapq.heapify(heap)
        
        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            for pair in lo[1:]:
                pair[1] = '0' + pair[1]
            for pair in hi[1:]:
                pair[1] = '1' + pair[1]
            heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
        
        codes = {}
        for pair in heap[0][1:]:
            byte = pair[0]
            code = [int(bit) for bit in pair[1]]
            codes[byte] = code
        
        return codes

    def compress_file(self, input_path: str, output_path: str) -> None:
        """Compress a single file to GAFO format"""
        with open(input_path, 'rb') as f:
            data = f.read()
        
        compressed = self._adaptive_huffman_encode(self._lz77_compress(data))
        
        with open(output_path, 'wb') as f:
            # Write GAFO header
            f.write(b'GAFO')
            f.write(struct.pack('>B', self.compression_level))
            
            # Write original file size
            f.write(struct.pack('>Q', len(data)))
            
            # Write compressed data
            f.write(compressed)

    def create_archive(self, files: List[str], archive_path: str) -> None:
        """Create a GAFO archive containing multiple files"""
        entries = []
        compressed_data = bytearray()
        
        # Process each file
        for file_path in files:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            original_size = len(data)
            compressed = self._adaptive_huffman_encode(self._lz77_compress(data))
            
            entry = GAFOFileEntry(
                filename=os.path.basename(file_path),
                offset=len(compressed_data),
                size=original_size,
                compressed_size=len(compressed),
                is_compressed=True
            )
            
            entries.append(entry)
            compressed_data.extend(compressed)
        
        # Write archive file
        with open(archive_path, 'wb') as f:
            # Archive header
            f.write(b'GAFOARCH')
            f.write(struct.pack('>B', self.compression_level))
            f.write(struct.pack('>H', len(files)))  # Number of files
            
            # File entries
            for entry in entries:
                filename_bytes = entry.filename.encode('utf-8')
                f.write(struct.pack('>H', len(filename_bytes)))
                f.write(filename_bytes)
                f.write(struct.pack('>Q', entry.offset))
                f.write(struct.pack('>Q', entry.size))
                f.write(struct.pack('>Q', entry.compressed_size))
                f.write(struct.pack('>B', int(entry.is_compressed)))
            
            # Write compressed data
            f.write(compressed_data)

    def extract_archive(self, archive_path: str, output_dir: str) -> None:
        """Extract files from a GAFO archive"""
        with open(archive_path, 'rb') as f:
            # Read archive header
            header = f.read(8)
            if header != b'GAFOARCH':
                raise ValueError("Invalid GAFO archive format")
            
            compression_level = struct.unpack('>B', f.read(1))[0]
            num_files = struct.unpack('>H', f.read(2))[0]
            
            # Read file entries
            entries = []
            for _ in range(num_files):
                filename_len = struct.unpack('>H', f.read(2))[0]
                filename = f.read(filename_len).decode('utf-8')
                offset = struct.unpack('>Q', f.read(8))[0]
                size = struct.unpack('>Q', f.read(8))[0]
                compressed_size = struct.unpack('>Q', f.read(8))[0]
                is_compressed = bool(struct.unpack('>B', f.read(1))[0])
                
                entries.append(GAFOFileEntry(
                    filename=filename,
                    offset=offset,
                    size=size,
                    compressed_size=compressed_size,
                    is_compressed=is_compressed
                ))
            
            # Read compressed data
            archive_data = f.read()
        
        # Extract files
        for entry in entries:
            file_data = archive_data[entry.offset:entry.offset + entry.compressed_size]
            
            if entry.is_compressed:
                file_data = self._lz77_decompress(self._adaptive_huffman_decode(file_data))
            
            output_path = os.path.join(output_dir, entry.filename)
            with open(output_path, 'wb') as f:
                f.write(file_data)

    def _lz77_decompress(self, data: bytes) -> bytes:
        """Decompress LZ77 compressed data"""
        decompressed = bytearray()
        pos = 0
        
        while pos < len(data):
            if data[pos] & 0x80:  # Literal
                decompressed.append(data[pos + 1])
                pos += 2
            else:  # Token
                if pos + 1 >= len(data):
                    break
                
                offset = ((data[pos] & 0x7F) << 4) | ((data[pos + 1] >> 4) & 0x0F)
                length = (data[pos + 1] & 0x3F) + 3
                
                # Copy from sliding window
                start = len(decompressed) - offset
                for i in range(length):
                    decompressed.append(decompressed[start + i])
                
                pos += 2
        
        return bytes(decompressed)

    def _adaptive_huffman_decode(self, data: bytes) -> bytes:
        """Decode adaptive Huffman compressed data"""
        pos = 0
        
        # Read header
        num_symbols = data[pos]
        pos += 1
        
        freq = {}
        for _ in range(num_symbols):
            byte = data[pos]
            pos += 1
            count = struct.unpack('>H', data[pos:pos + 2])[0]
            pos += 2
            freq[byte] = count
        
        # Rebuild Huffman tree
        codes = self._build_huffman_codes(freq)
        code_map = {tuple(code): byte for byte, code in codes.items()}
        
        # Read encoded data
        bit_buffer = []
        decoded = bytearray()
        
        # Process all bytes except the last padding byte
        for byte in data[pos:-1]:
            for i in range(7, -1, -1):
                bit = (byte >> i) & 1
                bit_buffer.append(bit)
                
                current_code = tuple(bit_buffer)
                if current_code in code_map:
                    decoded.append(code_map[current_code])
                    bit_buffer = []
        
        # Handle padding (last byte indicates padding length)
        padding = data[-1]
        if padding > 0:
            byte = data[-2]
            for i in range(7, 7 - (8 - padding), -1):
                bit = (byte >> i) & 1
                bit_buffer.append(bit)
                
                current_code = tuple(bit_buffer)
                if current_code in code_map:
                    decoded.append(code_map[current_code])
                    bit_buffer = []
        
        return bytes(decoded)