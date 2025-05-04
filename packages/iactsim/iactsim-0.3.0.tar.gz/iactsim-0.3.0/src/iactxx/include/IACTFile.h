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

#include<unordered_map>
#include<cmath>
#include<random>

#include<eventio.h>

namespace eventio = iactxx::eventio;

namespace iactxx {

constexpr eventio::f32 CM_TO_MM = 10.f;
constexpr eventio::f32 M_TO_KM = 1e-3f;
constexpr eventio::f32 MIN_WAVELENGTH = 1.f;

// Approximation used for consistency with CORSIKA IACT extension
// maybe it would be better to access the CORSIKA atmospheric model somehow
namespace air_refraction_model {

    // Speed of light in vacuum (mm/ns)
    constexpr float c_vacuum = 299.792458;

    // Coefficients for the refractive index formula n = 1 + A * exp(B*h + C*h^2)
    constexpr float A = 0.0002814;
    constexpr float B = -0.0947982; // h_km
    constexpr float C = -0.00134614; // h_km^2

} // namespace air_refraction_model

inline float light_speed(float h_km) {
    // Calculate the exponent term
    float exponent_term = air_refraction_model::B * h_km + air_refraction_model::C * h_km * h_km;

    // Calculate the refractive index
    float n = 1.f + air_refraction_model::A * std::exp(exponent_term);

    // Return speed of light in air
    return air_refraction_model::c_vacuum / n;
}

/**
 * @struct TelescopeData
 * @brief Consolidates all data associated with a single telescope.
 */
struct TelescopeData {
    eventio::Bunches<eventio::f32> bunches; // Bunches arrays
    eventio::TelescopeDefinition<eventio::f32> definition; // Telescope definition (x,y,z,r)
    std::vector<size_t> eventFileOffsets; // Byte offset of the start of each event raw data block in the original file buffer.
    std::vector<size_t> eventMapping; // Starting index within the bunches arrays for each event (n_events+1 values).
    std::vector<bool> eventIsCompactFormat; // Flag indicating if the raw data format for each event was compact.
    std::vector<size_t> eventNumBunches; // Number of bunches belonging to each specific event.
    std::vector<eventio::u32> eventIDs; // Identifier for each event.
    size_t totalNumberOfBunches; // Total number of bunches

    // Default constructor
    TelescopeData() : totalNumberOfBunches(0) {}

    // Rule of 5 not needed since eventio::Bunches and eventio::TelescopeDefinition handle resources with vectors and unique_ptrs.
};

/**
 * @brief Class to handle files generated with CORSIKA IACT extension
 * 
 */
class IACTFile {

    public:
        using TelescopeMap = std::unordered_map<size_t, TelescopeData>;
    
    private:
        // File related attributes
        std::vector<eventio::uu8> data_;
        std::string filePath_;

        // Run-related attributes
        size_t bunchSize_;
        size_t nReuse_;
        size_t nShowers_;
        size_t runID_;
        std::vector<float> zenithRange_;
        std::vector<float> azimuthRange_;
        float observationLevel_;
        float lambdaMin_;
        float lambdaMax_;
        float arrang_;
        std::string inputCard_;

        // Porcessing related attributes
        eventio::u32 minNumberOfBunches_{1};
        std::vector<int> skipTelescopes_;
    
        // Telescope-related attributes
        TelescopeMap telescopesData_;
        int nTelescopes_;
    
        // Private methods
        void readData();
        void parseInputCard();
        void parseTelescopeDefinitions();
        void countBunches();
    
    public:
        // Special member functions
        IACTFile() = default;
        IACTFile(const IACTFile &other) = default;
        IACTFile& operator=(const IACTFile &other) = default;
        IACTFile(IACTFile&& other) = default;
        IACTFile& operator=(IACTFile&& other) = default;
        ~IACTFile() = default;
    
        // Set member functions
        void setFilePath(const char* file_path);
        void setFilePath(std::string file_path);
        void setTelescopesToSkip(std::vector<int> telescopes) { skipTelescopes_ = std::move(telescopes); }
        void setMinimumNumberOfBunches(eventio::u32 min_bunches) { minNumberOfBunches_ = min_bunches; }
    
        // Public Parsing Methods
        void parseBunches();
        void convertBunches();
    
        // Get member functions
        const std::string& getInputCard();
        inline int getFileSize() const { return data_.size(); }
        inline int getNumberOfEvents() const { return nReuse_ * nShowers_; }
        inline int getRunID() const { return runID_; }
        inline int getBunchSize() const { return bunchSize_; }
        inline float getLambdaMin() const { return lambdaMin_; }
        inline float getLambdaMax() const { return lambdaMax_; }
        inline float getObservationLevel() const { return observationLevel_; }
        inline float getAzimuthOffset() const { return arrang_; }
        inline const std::vector<float>& getZenithRange() const { return zenithRange_; }
        inline const std::vector<float>& getAzimuthRange() const { return azimuthRange_; }
        inline std::vector<float> getPointing() const;
        inline int getNumberOfTelescopes() const { return nTelescopes_; }

        // Single telescope getter
        inline const TelescopeData& getTelescopeData(int tel_id) const;
        inline const eventio::TelescopeDefinition<eventio::f32>& getTelescopeDefinition(int tel_id) const;
        inline const std::vector<size_t>& getTelescopeEventMapping(int tel_id) const;
        inline const std::vector<eventio::u32>& getTelescopeEventIDs(int tel_id) const;
        inline const eventio::Bunches<eventio::f32>& getTelescopeBunches(int tel_id) const;
        inline const std::vector<size_t>& getEventNumberOfBunches(int tel_id) const;
        inline size_t getTelescopeNumberOfBunches(int tel_id) const;
        inline size_t getTelescopeNumberOfEvents(int tel_id) const;
        inline eventio::Bunches<eventio::f32> getEventBunches(int tel_id, int event_index) const;

};
    
    
    inline std::vector<float> IACTFile::getPointing() const {
        if (zenithRange_.size() < 2 || azimuthRange_.size() < 2) {
            return {0.0f, 0.0f};
        }
        float avg_zenith = 0.5f * (zenithRange_[0] + zenithRange_[1]);
        float altitude = 90.0f - avg_zenith;
        float avg_azimuth = 0.5f * (azimuthRange_[0] + azimuthRange_[1]);
        float azimuth = avg_azimuth - arrang_ - 180.f;
        azimuth = std::fmod(azimuth, 360.0f);
        if (azimuth < 0.0f) {
            azimuth += 360.0f;
        }
        return {altitude, azimuth};
    }
    
    inline const TelescopeData& IACTFile::getTelescopeData(int tel_id) const {
        auto it = telescopesData_.find(tel_id);
        if (it == telescopesData_.end()) {
            throw std::runtime_error("Telescope ID " + std::to_string(tel_id) + " not found.");
        }
        return it->second;
    }
    
    inline const eventio::TelescopeDefinition<eventio::f32>& IACTFile::getTelescopeDefinition(int tel_id) const {
         return getTelescopeData(tel_id).definition;
    }
    
    inline size_t IACTFile::getTelescopeNumberOfBunches(int tel_id) const {
        return getTelescopeData(tel_id).totalNumberOfBunches;
    }
    
    inline size_t IACTFile::getTelescopeNumberOfEvents(int tel_id) const {
        return getTelescopeData(tel_id).eventIDs.size();
    }
    
    inline const std::vector<eventio::u32>& IACTFile::getTelescopeEventIDs(int tel_id) const {
         return getTelescopeData(tel_id).eventIDs;
    }
    
    inline const eventio::Bunches<eventio::f32>& IACTFile::getTelescopeBunches(int tel_id) const {
         return getTelescopeData(tel_id).bunches;
    }

    inline const std::vector<size_t>& IACTFile::getTelescopeEventMapping(int tel_id) const {
        return getTelescopeData(tel_id).eventMapping;
   }
    
    inline const std::vector<size_t>& IACTFile::getEventNumberOfBunches(int tel_id) const {
        return getTelescopeData(tel_id).eventNumBunches;
    }
    
    inline eventio::Bunches<eventio::f32> IACTFile::getEventBunches(int tel_id, int event_index) const
    {
        auto tel_data = getTelescopeData(tel_id);
        auto bunches = tel_data.bunches;
        auto n_bunches = getEventNumberOfBunches(tel_id)[event_index];

        eventio::Bunches<eventio::f32> event_bunches = eventio::Bunches<eventio::f32>(n_bunches);
        
        const auto start = tel_data.eventMapping[event_index];
    
        std::copy_n(       bunches.pos.get()+start, n_bunches, event_bunches.pos.get());
        std::copy_n(       bunches.dir.get()+start, n_bunches, event_bunches.dir.get());
        std::copy_n(      bunches.time.get()+start, n_bunches, event_bunches.time.get());
        std::copy_n(       bunches.zem.get()+start, n_bunches, event_bunches.zem.get());
        std::copy_n(   bunches.photons.get()+start, n_bunches, event_bunches.photons.get());
        std::copy_n(bunches.wavelength.get()+start, n_bunches, event_bunches.wavelength.get());
    
        return event_bunches;
    }

} // namespace iactxx