/*
 * Copyright (C) 2024- Davide Mollica <davide.mollica@inaf.it>
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * This file is part of iactsim.
 *
 * iactsim is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * iactsim is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with iactsim.  If not, see <https://www.gnu.org/licenses/>.
 */

#pragma once

#include <vector>
#include <cstring>
#include <iostream>
#include <regex>
#include <cstdint>
#include <memory>
#include <sstream>
#include <filesystem>
#include <fstream>
#include <zlib.h>
#include <stdexcept>
#include <type_traits>
#include <cassert>
#include <algorithm>
#include <cmath>

#ifdef USE_OPENMP
    #include <omp.h>
#endif

namespace iactxx::eventio 
{

// Useful types
using u8 = uint8_t;
using u16 = uint16_t;
using u32 = uint32_t;
using u64 = uint64_t;
using i16 = int16_t;
using i32 = int32_t;
using i64 = int64_t;
using f32 = float;

/**
 * @brief Uninitialized uint8_t
 * Allows saving time when initializing a std::vector whose elements are going to be overwritten.
 * Particulary useful for load_file() and decompress_gzip_file().
 * 
 * Adapted from https://mmore500.com/2019/12/11/uninitialized-char.html
 * 
 */
struct uu8 {
  uint8_t val;

  // Default constructor (leaves val uninitialized)
  uu8() { ;/* leaves val uninitialized */ }

  // Constructor from uint8_t
  explicit uu8(uint8_t v) : val(v) {} // Initializes val

  // Assignment operator from uint8_t
  uu8& operator=(uint8_t v) {
    val = v;
    return *this;
  }

  // Conversion to uint8_t
  operator uint8_t() const { return val; }
};

// Useful constants
enum ObjectType {
  RUN_HEADER = 1200,
  TELESCOPE_DEFINITION = 1201,
  EVENT_HEADER = 1202,
  TELESCOPE_DATA = 1204,
  PHOTONS = 1205,
  EVENT_END = 1209,
  RUN_END = 1210,
  INPUT_CARD = 1212,
  NONE = 0
};
constexpr u64 MARKER{3558836791};

constexpr unsigned char GZ_FIRST_BYTE{0x1f};
constexpr unsigned char GZ_SECOND_BYTE{0x8b};
constexpr std::size_t GZ_CHUNK_SIZE = 32768;

/**
 * @brief Check if a type is an 8-bit unsigned integer at compile time.
 * 
 * @tparam T type to be checked.
 */
template <typename T>
constexpr bool is_8bit_integer = std::is_integral_v<T> && sizeof(T) == 1 && std::is_unsigned_v<T>;

/**
 * @brief Check if a type is an unsigned integer at compile time.
 * 
 * @tparam T type to be checked.
 */
template <typename T>
constexpr bool is_unsigned_integer = std::is_integral_v<T> && std::is_unsigned_v<T>;

/**
 * @brief Check if a type is an integer at compile time.
 * 
 * @tparam T type to be checked.
 */
template <typename T>
constexpr bool is_integer = std::is_integral_v<T>;

/**
 * @brief Load a whole file into memory.
 * 
 * @tparam TData Data type of the returned vector/array.
 * @tparam TSize Data type of the updated array size.
 * @param file_path Path of the file.
 * @param size Size of the returned array.
 * @return std::vector<TData> Pointer to the read data.
 */
template<typename TData>
inline std::vector<TData>
load_file(
  const char* file_path
) 
{
  // Get file size in bytes
  std::filesystem::path input_file_path{file_path};
  std::uintmax_t file_size = std::filesystem::file_size(file_path);
  
  // Get pointer size
  constexpr std::size_t type_size = sizeof(TData);
  if (file_size % type_size != 0)
    throw(std::runtime_error("File size is not a multiple of the type size."));
  
  std::size_t num_elements = static_cast<std::size_t>(file_size / type_size);

  // Allocate memory
  std::vector<TData> buffer(num_elements);

  // Open file
  std::ifstream input_file(input_file_path, std::ios_base::binary);

  if (!input_file.is_open()) {
    throw std::runtime_error("Failed to open file: " + input_file_path.string());
  }

  // Read file
  input_file.read(reinterpret_cast<char*>(buffer.data()), file_size);

  if (!input_file) 
  {
    throw std::runtime_error(
        "Error reading file: " + input_file_path.string() +
        ". Only " + std::to_string(input_file.gcount()) + " bytes could be read."
    );
  }
  
  return buffer;
}

/**
 * @brief Decompress from source file until stream ends or EOF.
 * Throws if:
 *   - status is Z_MEM_ERROR, i.e. memory could not be allocated for processing;
 *   - status is Z_DATA_ERROR, i.e. the deflate data is invalid or incomplete;
 *   - status is Z_STREAM_ERROR, i.e. the stream is not initialized properly;
 *   - there is an error reading the file.
 * Adapted from https://www.zlib.net/zlib_how.html.
 * 
 * @tparam TData 
 * @tparam TSize 
 * @param file_path 
 * @param size 
 * @return std::vector<TData> 
 */
template<typename TData>
inline std::vector<TData>
decompress_gzip_file(
  const char* file_path
)
{   
  static_assert(sizeof(TData) == 1, "Template argument TData must be a byte-sized type (e.g., char, unsigned char, std::byte).");

  FILE* source = fopen(file_path, "rb");

  Bytef in[GZ_CHUNK_SIZE];
  Bytef out[GZ_CHUNK_SIZE];

  // Allocate inflate state
  z_stream stream;
  stream.zalloc = Z_NULL;
  stream.zfree = Z_NULL;
  stream.opaque = Z_NULL;
  stream.avail_in = 0;
  stream.next_in = Z_NULL;

  int status;
  status = inflateInit2(&stream, 16+MAX_WBITS); // only gzip files, add 32 to enable also zlib decoding
  if (status != Z_OK) {
      std::stringstream message;
      message << "Error decompressing file: " << file_path << "\nCheck the gzip file integrity."<< std::endl;
      throw std::runtime_error(message.str());
  }

  // Get file size in bytes
  std::filesystem::path input_file_path{file_path};
  std::uintmax_t file_size = std::filesystem::file_size(input_file_path);

  // Reasonable amount of memory for CORSIKA IACT files
  std::vector<TData> data;
  data.reserve(1.5*file_size);

  // Decompress until deflate stream ends or end of file
  unsigned have;
  do {
    stream.avail_in = fread(in, 1, GZ_CHUNK_SIZE, source);

    if (ferror(source)) {
        inflateEnd(&stream);
        std::stringstream message;
        message << "Error decompressing file: " << file_path << "\nCheck the gzip file integrity."<< std::endl;
        throw std::runtime_error(message.str());
    }
    
    if (stream.avail_in == 0)
        break;

    // Run inflate() on input until output buffer is not full
    stream.next_in = in;
    do {
        stream.avail_out = GZ_CHUNK_SIZE;
        stream.next_out = out;

        status = inflate(&stream, Z_NO_FLUSH);

        switch (status) {
          case Z_STREAM_ERROR:
            [[fallthrough]];
          case Z_NEED_DICT:
            status = Z_DATA_ERROR;
            [[fallthrough]];
          case Z_DATA_ERROR:
            [[fallthrough]];
          case Z_MEM_ERROR:
            inflateEnd(&stream);
            std::stringstream message;
            message << "Error decompressing file: " << file_path << "\nCheck the gzip file integrity."<< std::endl;
            throw std::runtime_error(message.str());
        }
        have = GZ_CHUNK_SIZE - stream.avail_out;
        data.insert(data.end(), out, out+have);
    } while (stream.avail_out == 0);

  } while (status != Z_STREAM_END);

  // Clean up inflate state
  inflateEnd(&stream);

  data.shrink_to_fit();

  return data;
}

/**
 * @brief Check if a file is gzipped.
 * 
 * @param file_path Path of the file.
 * @return true If the file is gzipped.
 * @return false If the file is not gzipped.
 */
static inline bool is_gzipped(const char* file_path)
{
  if (!std::filesystem::exists(std::filesystem::path{file_path})) {
    std::stringstream message;
    message << "Error opening file: " << file_path << std::endl;
    throw std::runtime_error(message.str());
  }

  unsigned char buffer[2];
  std::ifstream input_file(file_path, std::ios_base::binary);
  input_file.read(reinterpret_cast<char*>(buffer), 2);
  input_file.close();

  return (buffer[0] == GZ_FIRST_BYTE) && (buffer[1] == GZ_SECOND_BYTE);
}

/**
 * @brief Unpack bits of an unsigned integer.
 * 
 * @tparam Tuint Unsigned integer type.
 * @param value Unsigned integer value.
 * @return u8* Unpacked bits.
 */
template<typename Tuint>
static inline u8* unpack_unisgned(const Tuint& value)
{
  static_assert(is_unsigned_integer<Tuint>, "Template argument must be an unsigned integer type.");

  constexpr int n_bits = sizeof(Tuint)*8;
  u8* bits[n_bits];
  for (int i=0; i<n_bits; ++i) {
    bits[i] = (value & (Tuint(1) << i)) == (Tuint(1) << i);
  }
  return bits;
}

/**
 * @brief Convert from bits to unsigned integer using an index value and a length value and assuming big-endian bits order.
 * 
 * @tparam Tuint Type of the output unisgned integer.
 * @param bits Array of bits.
 * @param start First bit.
 * @param nbit Number of bits.
 * @return Tuint Converted unsigned integer value.
 */
template<typename Tuint>
static inline Tuint 
bits_to_unsigned(
  const u8* bits,
  const int start,
  const int nbit)
{
  static_assert(is_unsigned_integer<Tuint>, "Template argument must be an unsigned integer type.");

  Tuint value{0};
  int end = start + nbit;
  for (int i=start; i<end; ++i) 
    value += (bits[i] << i);
  return value;
}

/**
 * @brief Extracts bits from an unsigned integer using an index value and a length value.
 * The extracted bits start from the least significant bit and all higher order bits are zeroed.
 * 
 * @tparam TExtr Return type of the extracted bits.
 * @tparam TSource Input type
 * @param src Unsigned integer from which extract bits
 * @param start Index of the first bit to be extracted
 * @param len Number of bits to be extracted
 * @return TExtr Extracted bits.
 */
template<typename TExtr, typename TSource>
static inline TExtr 
extract_bits_usigned(
  const TSource& src,
  const int start,
  const int len
)
{
  return static_cast<TExtr>((src >> start) & ((1 << len) - 1));
}

/**
 * @brief Extracts bits from an unsigned integer using an index value and a length value and store the result.
 * The extracted bits are written to the destination starting from the least significant bit. All higher order bits in the result are zeroed.
 * 
 * @tparam Tdest Destination type
 * @tparam Tuint Input type
 * @param src Unsigned integer from which extract bits
 * @param dest Where to store the extracted bits
 * @param start Index of the first bit to be extracted
 * @param len Number of bits to be extracted
 */
template<typename Tdest, typename Tuint>
static inline void
extract_bits_usigned(
  const Tuint& src,
  Tdest& dest,
  const int start,
  const int len
)
{
  static_assert(is_unsigned_integer<Tuint>, "Template argument must be an unsigned integer type.");

  dest = (src >> start) & ((1 << len) - 1);
}

/**
 * @brief Extract a bit as a boolean value from an unsigned integer.
 * 
 * @tparam Tuint Unsigned integer type.
 * @param src Unsigned integer value.
 * @param position Position of the bit.
 * @return bool 
 */
template<typename Tuint>
static inline bool
bool_from_bit(
    Tuint& src,
    const int position
)
{ 
  static_assert(is_unsigned_integer<Tuint>, "Template argument must be an unsigned integer type.");

  // Zero (i.e. the bit is 0) is converted to false,
  // any other value (i.e. the bit is 1) is converted to true
  return src & (1 << position);
}

/**
 * @brief Object header.
 * 
 */
struct ObjectHeader
{
  u64 length;
  u64 address;
  u32 marker;
  u32 id;
  u16 type;
  u16 version;
  u16 header_size;
  bool only_sub_objects;
  bool extended;
};

/**
 * @brief Parse an object header.
 * 
 * @tparam Corsika fila data type.
 * @param obj ObjectHeader where to store info.
 * @param data Corsika file data array.
 * @param position Header position inside data array.
 */
template<typename T>
static inline void 
decode_object_header(
  ObjectHeader& obj,
  T& data,
  const int position
)
{
  u16 buffer16;
  u64 buffer64;

  // Bytes 0-3 
  u32 first_4byte;
  memcpy(&first_4byte, &data[position], 4);
  
  int off = 0;

  // Main object
  if (first_4byte == MARKER) {
    obj.header_size = 16;
    obj.marker = first_4byte;
    
    //// Next four bytes
    // Bytes 4-5
    memcpy(&obj.type, &data[position+4], 2);
    //
    // Bits 4-15 of the bytes 6-7
    memcpy(&buffer16, &data[position+6], 2);
    obj.version = extract_bits_usigned<u16>(buffer16, 4, 11);
    obj.extended = bool_from_bit(buffer16, 1);
  
  // Sub-object
  } else {
    obj.marker = 0;
    obj.header_size = 12;
    // First four bytes
    extract_bits_usigned(first_4byte, obj.type, 0, 16);
    obj.extended = bool_from_bit(first_4byte, 17);
    extract_bits_usigned(first_4byte, obj.version, 20, 12);
    off = 4;
  }

  obj.address = position + obj.header_size;

  // Next four bytes
  memcpy(&obj.id, &data[position+8-off], 4);
  
  // Next four bytes
  memcpy(&buffer64, &data[position+12-off], 4);
  extract_bits_usigned(buffer64, obj.length, 0, 30);
  obj.only_sub_objects = bool_from_bit(buffer64, 30);

  // Next four bytes if there is an extention
  if (obj.extended) {
    obj.header_size += 4;
    u64 length_ext;
    // Read length extention into length_ext
    memcpy(&buffer64, &data[position+16-off], 4);
    extract_bits_usigned(buffer64, length_ext, 0, 12);
    // Extend length
    obj.length = obj.length | (length_ext<<30);
  }
}

template<typename TTelData>
struct TelescopeDefinition {
  TTelData x;
  TTelData y;
  TTelData z;
  TTelData r;
};

/**
 * @brief Bunch position.
 * 
 * @tparam T Data type.
 */
template <typename T> 
struct BunchPosition { 
  T x;
  T y;
  T z;
};

/**
 * @brief Bunch direction.
 * 
 * @tparam T Data type.
 */
template <typename T> 
struct BunchDirection { 
  T cx;
  T cy;
  T cz;
};

// TODO: use explicit names
/**
 * @brief Bunches data.
 * 
 * @tparam T Data type.
 */
template <typename T> 
class Bunches {
  public:
    u32 n_bunches;
    std::unique_ptr<BunchPosition<T>[]> pos;
    std::unique_ptr<BunchDirection<T>[]> dir;
    std::unique_ptr<T[]> time;
    std::unique_ptr<T[]> zem;
    std::unique_ptr<T[]> photons;
    std::unique_ptr<T[]> wavelength;

    // Special member functions
    Bunches() = default;
    explicit Bunches(int size)
    {
      n_bunches = size;
      pos.reset(new BunchPosition<T>[size]);
      dir.reset(new BunchDirection<T>[size]);
      time.reset(new T[size]);
      zem.reset(new T[size]);
      photons.reset(new T[size]);
      wavelength.reset(new T[size]);
    };
    Bunches(const Bunches &other) // Required by unique_ptr
    {
      *this = other;
    }
    Bunches& operator=(const Bunches<T> &other) // Required by unique_ptr
    {
      if (this != &other) copy(other);
      return *this;
    }
    Bunches(Bunches&& other) = default;
    Bunches& operator=(Bunches&& other) = default;
    ~Bunches() = default;
  
  private:
    inline void copy(const Bunches<T> &other) {
      n_bunches = other.n_bunches;

      pos = std::make_unique<BunchPosition<T>[]>(n_bunches);
      std::copy_n(other.pos.get(), n_bunches, pos.get());

      dir = std::make_unique<BunchDirection<T>[]>(n_bunches);
      std::copy_n(other.dir.get(), n_bunches, dir.get());

      time = std::make_unique<T[]>(n_bunches);
      std::copy_n(other.time.get(), n_bunches, time.get());

      zem = std::make_unique<T[]>(n_bunches);
      std::copy_n(other.zem.get(), n_bunches, zem.get());

      photons = std::make_unique<T[]>(n_bunches);
      std::copy_n(other.photons.get(), n_bunches, photons.get());

      wavelength = std::make_unique<T[]>(n_bunches);
      std::copy_n(other.wavelength.get(), n_bunches, wavelength.get());
    }
};

/**
 * @brief Read compact bunches and store the data in a Bunches object 
 * starting from a certain position. The Bunches object 
 * is not resized and can contain more than a event 
 * (if the Bunches object has been properly resized before).
 * 
 * @tparam T Corsika file data type.
 * @tparam B Bunches data type.
 * @param bunches Bunches struct where to store data.
 * @param index Start index.
 * @param n_bunches Number of bunches to be stored.
 * @param data Corsika file data array.
 * @param position Bunches position inside file-data array.
 * 
 */
template<typename T, typename B>
static inline void 
parse_compact_bunches(
  Bunches<B>& bunches,
  u32 index,
  u32 n_bunches,
  const T& data,
  int position
)
{ 
  constexpr size_t BUNCH_RECORD_SIZE = 16;
  constexpr size_t ENTRY_SIZE = 2;
  constexpr size_t POS_X_OFFSET = 12;
  constexpr size_t POS_Y_OFFSET = 14;
  constexpr size_t DIR_X_OFFSET = 16;
  constexpr size_t DIR_Y_OFFSET = 18;
  constexpr size_t TIME_OFFSET = 20;
  constexpr size_t ZEM_OFFSET = 22;
  constexpr size_t PHOTONS_OFFSET = 24;
  constexpr size_t WAVELENGTH_OFFSET = 26;

  constexpr B POS_SCALE = static_cast<B>(0.1);
  constexpr B DIR_SCALE = static_cast<B>(1. / 30000.);
  constexpr B DIR_CLAMP_MIN = static_cast<B>(-1.);
  constexpr B DIR_CLAMP_MAX = static_cast<B>(1.);
  constexpr B TIME_SCALE = static_cast<B>(0.1);
  constexpr B ZEM_EXP_SCALE = static_cast<B>(0.001);
  constexpr B ZEM_BASE = static_cast<B>(10.);
  constexpr B PHOTONS_SCALE = static_cast<B>(0.01);

  const std::byte* base_data_ptr = reinterpret_cast<const std::byte*>(data) + position;

  i16 x, y, cx, cy, time, zem, photons, wavelength;
  u32 end = index + n_bunches;
  u32 k = 0;
  
  for (u32 i=index; i<end; ++i) {
    const std::byte* current_bunch_base_ptr = base_data_ptr + k * BUNCH_RECORD_SIZE;

    // Get bunches from buffer
    std::memcpy(&x,          current_bunch_base_ptr + POS_X_OFFSET,      ENTRY_SIZE);
    std::memcpy(&y,          current_bunch_base_ptr + POS_Y_OFFSET,      ENTRY_SIZE);
    std::memcpy(&cx,         current_bunch_base_ptr + DIR_X_OFFSET,      ENTRY_SIZE);
    std::memcpy(&cy,         current_bunch_base_ptr + DIR_Y_OFFSET,      ENTRY_SIZE);
    std::memcpy(&time,       current_bunch_base_ptr + TIME_OFFSET,       ENTRY_SIZE);
    std::memcpy(&zem,        current_bunch_base_ptr + ZEM_OFFSET,        ENTRY_SIZE);
    std::memcpy(&photons,    current_bunch_base_ptr + PHOTONS_OFFSET,    ENTRY_SIZE);
    std::memcpy(&wavelength, current_bunch_base_ptr + WAVELENGTH_OFFSET, ENTRY_SIZE);

    // Position
    bunches.pos[i].x = static_cast<B>(x) * POS_SCALE;
    bunches.pos[i].y = static_cast<B>(y) * POS_SCALE;

    // Direction
    bunches.dir[i].cx = std::clamp(static_cast<B>(cx) * DIR_SCALE, DIR_CLAMP_MIN, DIR_CLAMP_MAX);
    bunches.dir[i].cy = std::clamp(static_cast<B>(cy) * DIR_SCALE, DIR_CLAMP_MIN, DIR_CLAMP_MAX);

    // Arrival time
    bunches.time[i] = static_cast<B>(time) * TIME_SCALE;

    // Emission altitude
    bunches.zem[i] = std::pow(ZEM_BASE, static_cast<B>(zem) * ZEM_EXP_SCALE);

    // Photons
    bunches.photons[i] = static_cast<B>(photons) * PHOTONS_SCALE;

    // Wavelength
    bunches.wavelength[i] = static_cast<B>(wavelength);

    k += 1;
  }
}

/**
 * @brief Read bunches and store the data in a Bunches object 
 * starting from a certain position. The Bunches object 
 * is not resized and can contain more than a event 
 * (if the Bunches object has been properly resized before).
 * 
 * @tparam T Corsika file data type (u8 or similar).
 * @tparam B Bunches data type.
 * @param bunches Bunches struct where to store data.
 * @param index Start index.
 * @param n_bunches Number of bunches to be stored.
 * @param data Corsika file data array.
 * @param position Bunches position inside file-data array.
 * 
 */
template<typename T, typename B>
static inline void 
parse_bunches(
  Bunches<B>& bunches,
  u32 index,
  u32 n_bunches,
  const T& data,
  int position
)
{ 
  constexpr size_t BUNCH_RECORD_SIZE = 32;
  constexpr size_t ENTRY_SIZE = 4;
  constexpr size_t POS_X_OFFSET = 12;
  constexpr size_t POS_Y_OFFSET = 16;
  constexpr size_t DIR_X_OFFSET = 20;
  constexpr size_t DIR_Y_OFFSET = 24;
  constexpr size_t TIME_OFFSET = 28;
  constexpr size_t ZEM_OFFSET = 32;
  constexpr size_t PHOTONS_OFFSET = 36;
  constexpr size_t WAVELENGTH_OFFSET = 40;

  const std::byte* base_data_ptr = reinterpret_cast<const std::byte*>(data) + position;

  u32 end = index + n_bunches;
  u32 k = 0;
  for (u32 i=index; i<end; ++i) {
    const std::byte* current_bunch_base_ptr = base_data_ptr + k * BUNCH_RECORD_SIZE;

    // Get bunches from buffer
    std::memcpy(&bunches.pos[i].x,      current_bunch_base_ptr + POS_X_OFFSET,      ENTRY_SIZE);
    std::memcpy(&bunches.pos[i].y,      current_bunch_base_ptr + POS_Y_OFFSET,      ENTRY_SIZE);
    std::memcpy(&bunches.dir[i].cx,     current_bunch_base_ptr + DIR_X_OFFSET,      ENTRY_SIZE);
    std::memcpy(&bunches.dir[i].cy,     current_bunch_base_ptr + DIR_Y_OFFSET,      ENTRY_SIZE);
    std::memcpy(&bunches.time[i],       current_bunch_base_ptr + TIME_OFFSET,       ENTRY_SIZE);
    std::memcpy(&bunches.zem[i],        current_bunch_base_ptr + ZEM_OFFSET,        ENTRY_SIZE);
    std::memcpy(&bunches.photons[i],    current_bunch_base_ptr + PHOTONS_OFFSET,    ENTRY_SIZE);
    std::memcpy(&bunches.wavelength[i], current_bunch_base_ptr + WAVELENGTH_OFFSET, ENTRY_SIZE);

    k += 1;
  }
}

/**
 * @brief Get values of a CORSIKA option from the input card string. 
 * Booleans are replaced with (T)0 and (T)1.
 * 
 * @tparam T Type of the values.
 * @param key Option keyword (e.g. "CSCAT").
 * @param input_card std::string containing the input card.
 * @return std::vector<T> Option values.
 */
template<typename T>
static inline std::vector<T>
get_from_input_card(
  std::string key,
  const std::string& input_card
)
{
  auto start = input_card.find(key);
  auto end = input_card.find("\n", start+1);

  auto key_row = input_card.substr(start, end-start);
  key_row = std::regex_replace(key_row, std::regex(" F "), " 0 ");
  key_row = std::regex_replace(key_row, std::regex(" T "), " 1 ");
  
  std::regex words_regex("[-+]?(?:\\d+\\.?\\d*|\\.\\d+)(?:[eE][-+]?\\d+)?");
  auto words_begin = std::sregex_iterator(key_row.begin(), key_row.end(), words_regex);
  auto words_end = std::sregex_iterator();

  std::vector<T> values;
  for (std::sregex_iterator i = words_begin; i != words_end; ++i)
      {
          float value = std::stof((*i).str());
          values.push_back(static_cast<T>(value));
  }
  return values;
}

} // end iactxx::eventio namespace

/**
 * @brief Overload ostream operator<< for ObjectHeader struct.
 * 
 * @param output Output stream.
 * @param object_header An ObjectHeader.
 * @return std::ostream& 
 */
static inline std::ostream &operator<<(std::ostream &output, const iactxx::eventio::ObjectHeader &object_header)
{
    output << "Marker\t\t" << object_header.marker << std::endl;
    output << "Object type\t" << object_header.type << std::endl;
    output << "Object version\t" << object_header.version << std::endl;
    output << "Identifier\t" << object_header.id << std::endl;
    output << "Length\t\t" << object_header.length << std::endl;
    output << std::boolalpha << "Only sub-obj\t" << object_header.only_sub_objects << std::endl;
    output << "Header size\t" << object_header.header_size << std::endl;
    output << "Address\t\t" << object_header.address << std::endl;
    output << "Extended\t" << object_header.extended << std::endl;
    return output;
}

/**
 * @brief Overload ostream operator<< for Bunches struct.
 * 
 * @tparam T Bunches data type.
 * @param output Output stream.
 * @param bunches A Bunches.
 * @return std::ostream& 
 */
template<typename T>
static inline std::ostream &operator<<(std::ostream &output, const iactxx::eventio::Bunches<T> &bunches)
{
    auto n_bunches = bunches.n_bunches;

    for (std::size_t i=0; i<n_bunches; ++i) {
        output << bunches.pos[i].x << "\t"
               << bunches.pos[i].y << "\t"
               << bunches.pos[i].z << "\t"
               << bunches.dir[i].cx << "\t"
               << bunches.dir[i].cy << "\t"
               << bunches.time[i] << "\t"
               << bunches.zem[i] << "\t"
               << bunches.photons[i] << "\t"
               << bunches.wavelength[i]
               << "\n";
    }
    output << std::endl;
    return output;
}

