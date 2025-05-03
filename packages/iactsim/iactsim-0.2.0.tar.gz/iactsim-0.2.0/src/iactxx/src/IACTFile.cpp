// Copyright (C) 2024- Davide Mollica <davide.mollica@inaf.it>
// SPDX-License-Identifier: GPL-3.0-or-later
//
// This file is part of iactsim.
//
// iactsim is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// iactsim is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with iactsim.  If not, see <https://www.gnu.org/licenses/>.

#include <IACTFile.h>

#include <iostream>

namespace iactxx {

/**
 * @brief Read data from file.
 * 
 */
void IACTFile::readData()
{
    if (eventio::is_gzipped(filePath_.c_str())) {
        data_ = eventio::decompress_gzip_file<eventio::uu8>(filePath_.c_str());
    }
    else {
        data_ = eventio::load_file<eventio::uu8>(filePath_.c_str());
    }
}

void IACTFile::setFilePath(std::string file_path)
{
    setFilePath(file_path.c_str());
}

/**
 * @brief Set the file path and read the file,
 * then parse the input card to extract a minimal set of info.
 *
 * @param file_path
 */
void IACTFile::setFilePath(const char* file_path)
{
    filePath_ = file_path;

    telescopesData_.clear();

    // Read the following:
    // data_
    readData();

    // Read the following:
    // nReuse_, nShowers_, runID_,
    // inputCard_, bunchSize_, etc.
    parseInputCard();

    // Get telescopes definition
    parseTelescopeDefinitions();

    int nEvents = nShowers_*nReuse_;
    for (auto& pair : telescopesData_) {
        TelescopeData& tel_data = pair.second;
        tel_data.eventNumBunches.reserve(nEvents);
        tel_data.eventMapping.reserve(nEvents + 1);
        tel_data.eventFileOffsets.reserve(nEvents);
        tel_data.eventIsCompactFormat.reserve(nEvents);
        tel_data.eventIDs.reserve(nEvents);
    }

    // Count bunches
    countBunches();
}

/**
 * @brief Parses the TELESCOPE_DEFINITION object.
 */
void IACTFile::parseTelescopeDefinitions()
{
    size_t position{0};
    eventio::ObjectHeader object;
    object.type = eventio::NONE;
    eventio::i32 n_telescopes;

    nTelescopes_ = 0;

    auto data = data_.data();
    auto file_size = data_.size();
    bool found_definition = false;

    while (object.type != eventio::TELESCOPE_DEFINITION) {

        eventio::decode_object_header(object, data, position);

        // std::cout << object << std::endl;

        position += object.header_size;

        if (object.type == eventio::TELESCOPE_DEFINITION) {
            found_definition = true;
            memcpy(&n_telescopes, &data[position], 4);
            nTelescopes_ = n_telescopes;
            position += 4;

            for (int tel_id = 0; tel_id < n_telescopes; ++tel_id) {

                // Add a new telescope
                TelescopeData& tel_data = telescopesData_[tel_id];
                
                size_t n_tel_size_t = static_cast<size_t>(n_telescopes);
                size_t tel_id_size_t = static_cast<size_t>(tel_id);
                constexpr size_t DATA_SIZE = 4;
                constexpr size_t N_ENTRIES = 4;

                memcpy(&tel_data.definition.x, &data[position +                   tel_id_size_t*N_ENTRIES], DATA_SIZE);
                memcpy(&tel_data.definition.y, &data[position + n_tel_size_t*4  + tel_id_size_t*N_ENTRIES], DATA_SIZE);
                memcpy(&tel_data.definition.z, &data[position + n_tel_size_t*8  + tel_id_size_t*N_ENTRIES], DATA_SIZE);
                memcpy(&tel_data.definition.r, &data[position + n_tel_size_t*12 + tel_id_size_t*N_ENTRIES], DATA_SIZE);
            
            }
        }

        position += object.length;

        if (position > file_size) {
             if (!found_definition) {
                  throw(std::runtime_error("No telescope defintion object (1201) found."));
             }
             break;
        }
    }
     if (!found_definition && position >= file_size) {
          throw(std::runtime_error("No telescope defintion object (1201) found."));
     }
}

/**
 * @brief Counts bunches per event and populates vectors in telescopeData_.
 */
void IACTFile::countBunches()
{
    for (auto& pair : telescopesData_) {
        TelescopeData& tel_data = pair.second;
        tel_data.eventNumBunches.clear();
        tel_data.eventMapping.clear();
        tel_data.eventMapping.push_back(0);
        tel_data.eventFileOffsets.clear();
        tel_data.eventIsCompactFormat.clear();
        tel_data.eventIDs.clear();
        tel_data.totalNumberOfBunches = 0;
    }

    size_t position{0};
    eventio::ObjectHeader object;
    eventio::u32 n_bunches;
    eventio::u32 shower_id{};
    eventio::u32 event_id;
    int tel_id;
    bool compact;

    auto data = data_.data();
    auto file_size = data_.size();

    while (position < file_size) {
        
        eventio::decode_object_header(object, data, position);

        // std::cout << object << std::endl;

        // Found an EVENT_HEADER (should be before the PHOTONS objects)
        if (object.type == eventio::EVENT_HEADER)
            shower_id = object.id;
        
        // Move to the data field (or to the first sub-object)
        position += object.header_size;

        // Count bunches
        if (object.type == eventio::PHOTONS) {
            constexpr size_t N_BUNCHES_OFFSET = 8;
            constexpr size_t N_BUNCHES_BYTES = 4;
            memcpy(&n_bunches, &data[position+N_BUNCHES_OFFSET], N_BUNCHES_BYTES);

            if (n_bunches >= minNumberOfBunches_) {
                compact = object.version / 1000 == 1;
                event_id = shower_id*100 + object.id/1000;
                tel_id = object.id % 1000;

                TelescopeData& tel_data = telescopesData_[tel_id];
                tel_data.eventIDs.push_back(event_id);
                tel_data.eventNumBunches.push_back(n_bunches);
                tel_data.eventFileOffsets.push_back(position);
                tel_data.eventIsCompactFormat.push_back(compact);
                tel_data.totalNumberOfBunches += n_bunches;
                tel_data.eventMapping.push_back(tel_data.totalNumberOfBunches);
            }
        }

        // Move to the next object
        if (!object.only_sub_objects) {
            position += object.length;
        }
    }
}

/**
 * @brief Parses the actual photon bunch data from the file buffer.
 */
void IACTFile::parseBunches()
{
    auto data = data_.data();

    for (auto& pair : telescopesData_)
    {
        // Check if the telescope can be skipped
        auto it = std::find(skipTelescopes_.begin(), skipTelescopes_.end(), pair.first);
        bool found = (it != skipTelescopes_.end());
        if (found == true) continue;

        TelescopeData& tel_data = pair.second;

        if (tel_data.totalNumberOfBunches == 0) {
             tel_data.bunches = eventio::Bunches<eventio::f32>();
             continue;
        }

        tel_data.bunches = eventio::Bunches<eventio::f32>(tel_data.totalNumberOfBunches);

        size_t n_events = tel_data.eventIDs.size();

        for (size_t event=0; event<n_events; ++event) {
            size_t position_in_data = tel_data.eventFileOffsets[event];
            size_t n_bunches = tel_data.eventNumBunches[event];
            size_t index_in_array = tel_data.eventMapping[event];
            bool is_compact = tel_data.eventIsCompactFormat[event];

            if (is_compact) {
                eventio::parse_compact_bunches(tel_data.bunches, index_in_array, n_bunches, data, position_in_data);
            } else {
                eventio::parse_bunches(tel_data.bunches, index_in_array, n_bunches, data, position_in_data);
            }

        }
    }
}

void IACTFile::convertBunches()
{
    // Obs. level is in m, here converted to km
    float inv_speed_light = 1.f / light_speed(observationLevel_*M_TO_KM);

    // For wavelength generation (if necessary)
    const double inv_lmin = 1.f / lambdaMin_;
    const double inv_lmax = 1.f / lambdaMax_;
    const double inv_ldiff = inv_lmin - inv_lmax;
    std::random_device rd;
    std::mt19937 gen(rd());

    for (auto& pair : telescopesData_)
    {
        int tel_id = pair.first;
        TelescopeData& tel_data = pair.second;

        // Check if the telescope can be skipped
        auto it = std::find(skipTelescopes_.begin(), skipTelescopes_.end(), tel_id);
        bool found = (it != skipTelescopes_.end());
        if (found == true) continue;
        
        auto pos = tel_data.bunches.pos.get();
        auto dir = tel_data.bunches.dir.get();
        auto zem = tel_data.bunches.zem.get();
        auto time = tel_data.bunches.time.get();
        auto wl = tel_data.bunches.wavelength.get();

        eventio::f32 z0 = tel_data.definition.z*CM_TO_MM;

        size_t n_bunches = static_cast<size_t>(tel_data.bunches.n_bunches);
        
        // Convert to mm
        for (size_t i=0; i<n_bunches; i++) {
            pos[i].x *= CM_TO_MM; // to mm
            pos[i].y *= CM_TO_MM; // to mm
            zem[i] *= CM_TO_MM; // to mm
        }

        #pragma omp simd
        for (size_t i=0; i<n_bunches; i++) {
            // Compute z direction
            dir[i].cz = -std::sqrt(1.f - dir[i].cx*dir[i].cx - dir[i].cy*dir[i].cy);

            // Move from the observational level to the telescope altitude
            eventio::f32 dist = z0 / dir[i].cz; // negative distance
            pos[i].z = z0;
            pos[i].x += dist*dir[i].cx;
            pos[i].y += dist*dir[i].cy;

            // Update time
            time[i] += dist * inv_speed_light;
        }

        for (size_t i=0; i<n_bunches; i++) {
            // Assuming wavelength <= 0 means "undefined", generate from a Cherenkov spectrum
            if (wl[i] < MIN_WAVELENGTH) {
                uint32_t raw_bits32 = gen();
                // Convert raw uint32_t to float in [0.0f, 1.0f) using ldexp(val, exp) = val * 2^exp
                float u = std::ldexp(static_cast<float>(raw_bits32), -32);
                // Transform to be uniform in [inv_lmax, inv_lmin)
                float transformed_inv_wl = u * inv_ldiff + inv_lmax;
                // Calculate final wavelength
                wl[i] = 1.f / transformed_inv_wl;
            }
        }
    }
}

void IACTFile::parseInputCard()
{
    int position{0};
    eventio::ObjectHeader object;
    object.type = eventio::NONE;
    eventio::u32 buffer32;
    eventio::i16 buffer16;
    eventio::i16 n_strings;
    int sub_pos;

    auto data = data_.data();

    std::stringstream input_card_stream;

    while (object.type != eventio::INPUT_CARD) {

        eventio::decode_object_header(object, data, position);

        // Move to the data field (or to the first sub-object)
        position += object.header_size;

        if (object.type == eventio::INPUT_CARD) {
            // Number of strings
            memcpy(&buffer32, &data[position], 4);
            n_strings = buffer32;
            
            // Read each string
            sub_pos = position + 4;
            for (int i=0; i<n_strings; ++i) {
                memcpy(&buffer16, &data[sub_pos], 2);
                std::string string(&data[sub_pos+2], &data[sub_pos+2+buffer16]);

                sub_pos += 2+buffer16;
                if (string.substr(0, 1) != "*")
                    input_card_stream << string << "\n";
            }
        }
        inputCard_ = input_card_stream.str();

        // Ignore sub-objects and move to the next object
        position += object.length;
    }
    
    // Get useful info for simulation handling
    runID_ = eventio::get_from_input_card<float>("RUNNR", inputCard_)[0];
    nReuse_ = eventio::get_from_input_card<float>("CSCAT", inputCard_)[0];
    nShowers_ = eventio::get_from_input_card<float>("NSHOW", inputCard_)[0];
    bunchSize_ = eventio::get_from_input_card<float>("CERSIZ", inputCard_)[0];
    zenithRange_ = eventio::get_from_input_card<float>("THETAP", inputCard_); // degree
    azimuthRange_ = eventio::get_from_input_card<float>("PHIP", inputCard_); // degree
    arrang_ = eventio::get_from_input_card<float>("ARRANG", inputCard_)[0]; // degree
    observationLevel_ = eventio::get_from_input_card<float>("OBSLEV", inputCard_)[0]*1e2f; // mm
    std::vector<float> lambdas = eventio::get_from_input_card<float>("CWAVLG", inputCard_); // nm
    lambdaMin_ = lambdas[0];
    lambdaMax_ = lambdas[1];
}

const std::string& IACTFile::getInputCard()
{
    parseInputCard();
    return inputCard_;
}

} // namespace iactxx