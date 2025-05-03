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

#include <string>

// Pybind11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Automatic vector conversions
#include <pybind11/numpy.h>

// Local headers
#include <arrays_ops.h>
#include <IACTFile.h>

namespace py = pybind11;

using BunchPosition = iactxx::eventio::BunchPosition<iactxx::eventio::f32>;
using BunchDirection = iactxx::eventio::BunchDirection<iactxx::eventio::f32>;

namespace iactxx {

inline static IACTFile read_file(
    const std::string& filepath,
    const std::vector<int> telescopes_to_skip,
    int min_n_bunches
) 
{
    IACTFile cfile;
    cfile.setTelescopesToSkip(telescopes_to_skip);
    cfile.setMinimumNumberOfBunches(min_n_bunches);
    cfile.setFilePath(filepath);
    cfile.parseBunches();
    cfile.convertBunches();
    return cfile;
}

inline static std::vector<IACTFile> read_files(
    const std::vector<std::string>& filepaths,
    const std::vector<int> telescopes_to_skip,
    int min_n_bunches
) 
{
    int n_files = filepaths.size();

    std::vector<IACTFile> cfiles;
    cfiles.resize(n_files);

    #pragma omp parallel for default(none) shared(cfiles, filepaths, telescopes_to_skip) firstprivate(n_files, min_n_bunches)
    for (int file_id=0; file_id<n_files; ++file_id)
    {
        IACTFile cfile;
        cfile.setTelescopesToSkip(telescopes_to_skip);
        cfile.setMinimumNumberOfBunches(min_n_bunches);
        cfile.setFilePath(filepaths[file_id]);
        cfile.parseBunches();
        cfile.convertBunches();
        cfiles[file_id] = std::move(cfile);
    }
    
    return cfiles;
}

namespace pybind
{

/**
 * @brief Create a float 3D array numpy view.
 * 
 * @tparam T Array type
 * @param ptr Array pointer
 * @param count Number of elements
 * @param owner Python object owning the memory
 * @return py::array 
 */
template <typename T>
inline py::array create_vec3f_numpy_view(
    const T* ptr,
    size_t count,
    py::object owner
) 
{
    // Check if T has a standard layout (i.e. stride assumptions are valid)
    static_assert(
        std::is_standard_layout<T>::value,
        "Template type T must have standard layout for reliable striding."
    );

    // Handle empty/null case -> return an empty NumPy array (copy, has no owner)
    if (!ptr || count == 0) {
        std::vector<ssize_t> empty_shape = {0, 3};
        return py::array(py::dtype("f4"), empty_shape);
    }

    // Define shape and strides based on T
    std::vector<ssize_t> shape = {(ssize_t)count, 3}; // N rows, 3 columns
    std::vector<ssize_t> strides = {
        (ssize_t)sizeof(T), // Bytes to stride to get to the next T (next row)
        (ssize_t)sizeof(float) // Bytes to stride to get to the next float within T (next column)
    };

    // Create the view
    return py::array(
        py::dtype("f4"), // float32
        shape,
        strides,
        ptr, // Pointer to the start of the first struct T
        owner // Python object owning the memory
    );
}

template <typename T>
inline py::array create_numpy_view(
    const T* ptr,
    size_t count,
    py::object owner
)
{
    // Determine the NumPy dtype format string based on the C++ type T
    const std::string format = py::format_descriptor<T>::format();
    const py::dtype dtype = py::dtype(format);

    // If source is invalid/empty return an empty NumPy array (copy, has no owner)
    if (!ptr || count == 0) {
        // Use py::ssize_t for shape dimensions
        std::vector<py::ssize_t> empty_shape = {0};
        // Return an empty array with the correct dtype
        return py::array(dtype, empty_shape);
    }

    // Define shape and strides for the 1D view using py::ssize_t
    std::vector<py::ssize_t> shape = {(py::ssize_t)count};

    // Stride is the size of one element of type T
    std::vector<py::ssize_t> strides = {(py::ssize_t)sizeof(T)};

    // Create the view
    return py::array(
        dtype,   // Deduced NumPy data type
        shape,   // Shape of the array (1D)
        strides, // Strides for the array (size of element)
        ptr,     // Pointer to the first element
        owner    // Python object owning the memory
    );
}

template <typename T>
py::array_t<T> add_numpy_arrays(
    py::array_t<T, py::array::c_style> arr1,
    py::array_t<T, py::array::c_style> arr2)
{
    // Request buffer information from the input arrays
    py::buffer_info buf1 = arr1.request();
    py::buffer_info buf2 = arr2.request();

    // Check if arrays have the same size in the first dimension
    if (buf1.shape.size() == 0 || buf2.shape.size() == 0 || buf1.shape[0] != buf2.shape[0]) {
         throw std::runtime_error("Input arrays must have the same size in the first dimension");
    }

    // Check for shape compatibility
    if (buf1.ndim > 1) {
        for(py::ssize_t i = 1; i < buf1.ndim; ++i) {
            if (buf1.shape[i] != buf2.shape[i]) {
                 throw std::runtime_error("Input arrays must have the same shape");
            }
        }
    }

    // Get the total number of elements
    size_t size = buf1.size;

    // Empty array case
    if (size == 0) {
        return py::array_t<T>(buf1.shape);
    }
    if (buf1.size != buf2.size) {
         throw std::runtime_error("Input arrays must have the same total number of elements");
    }

    // Create the result NumPy array with the same shape as the inputs
    py::array_t<T> result = py::array_t<T>(buf1.shape);
    py::buffer_info buf_result = result.request();

    // Get raw pointers to the buffer data
    T* ptr1 = static_cast<T*>(buf1.ptr);
    T* ptr2 = static_cast<T*>(buf2.ptr);
    T* ptr_result = static_cast<T*>(buf_result.ptr);

    iactxx::math::add(ptr1, ptr2, ptr_result, size);
    
    // Return the result array
    return result;
}

template <typename T>
void axpy_numpy_arrays(
    T scalar, // pybind will cast the scalar
    py::array_t<T, py::array::c_style> arr1,
    py::array_t<T, py::array::c_style> arr2)
{
    // Request buffer information from the input arrays
    py::buffer_info buf1 = arr1.request();
    py::buffer_info buf2 = arr2.request();

    // Check if arrays have the same size in the first dimension
    if (buf1.shape.size() == 0 || buf2.shape.size() == 0 || buf1.shape[0] != buf2.shape[0]) {
         throw std::runtime_error("Input arrays must have the same size in the first dimension");
    }

    // Check for shape compatibility
    if (buf1.ndim > 1) {
        for(py::ssize_t i = 1; i < buf1.ndim; ++i) {
            if (buf1.shape[i] != buf2.shape[i]) {
                 throw std::runtime_error("Input arrays must have the same shape");
            }
        }
    }

    // Get the total number of elements
    size_t size = buf1.size;

    // Empty array case
    if (size == 0) {
        return;
    }
    if (buf1.size != buf2.size) {
         throw std::runtime_error("Input arrays must have the same total number of elements");
    }

    // Get raw pointers to the buffer data
    T* ptr1 = static_cast<T*>(buf1.ptr);
    T* ptr2 = static_cast<T*>(buf2.ptr);

    iactxx::math::axpy(scalar, ptr1, ptr2, size);
    
    return;
}

} // namespace iactxx::pybind

} // namespace iactxx

template<typename... Ts>
void define_add_overloads(py::module_& m) {
    (
        m.def(
            "add",
            &iactxx::pybind::add_numpy_arrays<Ts>,
            "Adds two NumPy arrays element-wise.",
            py::arg("arr1").noconvert(),
            py::arg("arr2").noconvert()
        ),
        ...
    );
}

template<typename... Ts>
void define_axpy_overloads(py::module_& m) {
    (
        m.def(
            "axpy",
            &iactxx::pybind::axpy_numpy_arrays<Ts>,
            "Adds two NumPy arrays element-wise.",
            py::arg("scalar"),
            py::arg("arr1").noconvert(),
            py::arg("arr2").noconvert()
        ),
        ...
    );
}

// Define the Python module 'iactxx'
PYBIND11_MODULE(iactxx, m) {
    m.doc() = "pybind11 extension module for iactsim";

    /////////////////////////////////////////////////////
    //
    // math example submodule
    //
    /////////////////////////////////////////////////////

    // Create a submodule attached to 'm'
    py::module_ math_submodule = m.def_submodule(
        "math", // Python name of the submodule
        "Example submodule for basic math operations" // Docstring for the submodule
    );

    define_add_overloads
    <
    uint8_t, int8_t, uint16_t, int16_t,
    uint32_t, int32_t, uint64_t, int64_t,
    float, double
    >(math_submodule);

    define_axpy_overloads
    <
    uint8_t, int8_t, uint16_t, int16_t,
    uint32_t, int32_t, uint64_t, int64_t,
    float, double
    >(math_submodule);

    /////////////////////////////////////////////////////
    //
    // io submodule
    //
    /////////////////////////////////////////////////////
    
    // Create a submodule attached to 'm'
    py::module_ io_submodule = m.def_submodule(
        "io",
        "Submodule for io operations"
    );

    py::class_<iactxx::IACTFile>(
            io_submodule,
            "IACTFile",
            R"raw(
            Class that represents a file produced by CORSIKA IACT extension.
            )raw"
        )
        // Bind the constructor
        .def(py::init<>())

        // Set methods
        .def("set_filepath", py::overload_cast<std::string>(&iactxx::IACTFile::setFilePath), "Link to a file", py::arg("filepath"))
        .def("set_telescopes_to_skip", &iactxx::IACTFile::setTelescopesToSkip, "Set which telescopes can be skipped", py::arg("telescopes"))
        .def("set_minimum_number_of_bunches", &iactxx::IACTFile::setMinimumNumberOfBunches, "Set minimum number of bunches", py::arg("n_bunches"))

        // Read data
        .def("parse_bunches", &iactxx::IACTFile::parseBunches, "Read photon bunches")
        .def("convert_bunches", &iactxx::IACTFile::convertBunches, "Convert photon bunches units")

        // Get meothods
        .def("get_number_of_bunches", 
            [](iactxx::IACTFile& self){
                py::dict n_bunches_per_telescope;
                for (int i=0; i<self.getNumberOfTelescopes(); i++) {
                    const auto n_bunches = self.getTelescopeNumberOfBunches(i);
                    n_bunches_per_telescope[py::int_(i)] = n_bunches;
                }
                return n_bunches_per_telescope;
            },
            "Get number of bunches of all telescopes"
        )
        .def(
            "get_telescope_number_of_bunches",
            &iactxx::IACTFile::getTelescopeNumberOfBunches, 
            "Get number if bunches hitting the telescope with ID `tel_id`",
            py::arg("tel_id")
        )
        .def("get_input_card", &iactxx::IACTFile::getInputCard, "Get the the CORSIKA input card")
        .def("get_pointing", &iactxx::IACTFile::getPointing, "Get mean pointing direction")
        .def("get_bunch_size", &iactxx::IACTFile::getBunchSize, "Get number of photons per bunch")
        .def("get_lambda_min", &iactxx::IACTFile::getLambdaMin, "Get minimum simulated photon wavelength")
        .def("get_lambda_max", &iactxx::IACTFile::getLambdaMax, "Get minimum simulated photon wavelength")
        .def("get_zenith_range", &iactxx::IACTFile::getZenithRange, "Get minimum simulated photon wavelength")
        .def("get_azimuth_range", &iactxx::IACTFile::getAzimuthRange, "Get minimum simulated photon wavelength")
        .def("get_azimuth_offset", &iactxx::IACTFile::getAzimuthOffset, "Get azimuth offset w.r.t. CORSIKA reference system (geomagnetic north)")
        .def("get_number_of_telescopes", &iactxx::IACTFile::getNumberOfTelescopes, "Get number of simulated telescopes")
        .def("get_filesize", &iactxx::IACTFile::getFileSize, "Get file size (in byte)")
        .def("get_number_of_events", &iactxx::IACTFile::getNumberOfEvents, "Get total number of events (taking reused into account)")
        .def("get_event_number_of_bunches", &iactxx::IACTFile::getEventNumberOfBunches, "Get number of bunches of each event", py::arg("tel_id"))
        .def("get_telescope_event_ids", &iactxx::IACTFile::getTelescopeEventIDs, "Get identifier of each event", py::arg("tel_id"))
        .def(
            "get_telescope_bunches",
            [](iactxx::IACTFile &self, int tel_id) -> py::list {
                auto& bunches = self.getTelescopeBunches(tel_id);
                size_t size = bunches.n_bunches;
                const BunchPosition* pos_ptr = bunches.pos.get();
                const BunchDirection* dir_ptr = bunches.dir.get();
                const float* t_ptr = bunches.time.get();
                const float* wl_ptr = bunches.wavelength.get();
                const float* zem_ptr = bunches.zem.get();

                auto& bunches_mapping = self.getTelescopeEventMapping(tel_id);
                auto* map_ptr = bunches_mapping.data();

                // Create the non-copying NumPy array view
                // The 'base' object must be the Python object that owns
                // the 'self' C++ instance to manage lifetime correctly.
                // We get this Python object by casting the C++ reference 'self'.
                py::object py_self = py::cast(&self, py::return_value_policy::reference);

                // Create NumPy views
                py::array pos_view = iactxx::pybind::create_vec3f_numpy_view(pos_ptr, size, py_self);
                py::array dir_view = iactxx::pybind::create_vec3f_numpy_view(dir_ptr, size, py_self);
                py::array t_view = iactxx::pybind::create_numpy_view(t_ptr, size, py_self);
                py::array zem_view = iactxx::pybind::create_numpy_view(zem_ptr, size, py_self);
                py::array wl_view = iactxx::pybind::create_numpy_view(wl_ptr, size, py_self);
                py::array map_view = iactxx::pybind::create_numpy_view(map_ptr, bunches_mapping.size(), py_self);
                
                // Package them into a list
                py::list result_list;
                result_list.append(pos_view);
                result_list.append(dir_view);
                result_list.append(wl_view);
                result_list.append(t_view);
                result_list.append(zem_view);
                result_list.append(map_view);

                // Return the views
                return result_list;
            },
            R"raw(
            Returns bunches as a list of NumPy array view of photon positions, directions, 
            wavelengths, arrival times, emission altitudes and event mapping to be passed to :py:meth:`iactsim.IACT.trace_photons` method.

            For example, if ``cfile`` is a ``IACTFile`` instance and ``telescope`` a ``IACT`` instance:

                .. code-block:: python
                    
                    telescope.trace_photons(
                        *cfile.get_telescope_bunches(tel_id),
                        photons_per_bunch=cfile.get_bunch_size(),
                        simulate_camera=True
                    )
            
            )raw",
            py::arg("tel_id")
        )
        .def(
            "get_event_bunches",
            [](iactxx::IACTFile &self, int tel_id, int event) -> py::list {
                // Call the public accessors of the pure C++ class instance ('self')
                auto temp_bunches = self.getEventBunches(tel_id, event);
                size_t size = temp_bunches.n_bunches;
                BunchPosition* pos_ptr = temp_bunches.pos.get();
                BunchDirection* dir_ptr = temp_bunches.dir.get();
                const float* time_ptr = temp_bunches.time.get();
                const float* wl_ptr = temp_bunches.wavelength.get();
                const float* zem_ptr = temp_bunches.zem.get();
                
                std::vector<ssize_t> shape3d = {(ssize_t)size, 3};
                std::vector<ssize_t> shape1d = {(ssize_t)size};

                py::array_t<float> pos(shape3d);
                py::array_t<float> dir(shape3d);
                py::array_t<float> time(shape1d);
                py::array_t<float> wl(shape1d);
                py::array_t<float> zem(shape1d);

                py::buffer_info pos_buf_info = pos.request();
                float* pos_dest_ptr = static_cast<float*>(pos_buf_info.ptr);
                std::memcpy(
                    pos_dest_ptr,
                    pos_ptr,
                    size * sizeof(BunchPosition)
                );

                py::buffer_info dir_buf_info = dir.request();
                float* dir_dest_ptr = static_cast<float*>(dir_buf_info.ptr);
                std::memcpy(
                    dir_dest_ptr,
                    dir_ptr,
                    size * sizeof(BunchDirection)
                );

                py::buffer_info time_buf_info = time.request();
                float* time_dest_ptr = static_cast<float*>(time_buf_info.ptr);
                std::memcpy(
                    time_dest_ptr,
                    time_ptr,
                    size * sizeof(float)
                );

                py::buffer_info wl_buf_info = wl.request();
                float* wl_dest_ptr = static_cast<float*>(wl_buf_info.ptr);
                std::memcpy(
                    wl_dest_ptr,
                    wl_ptr,
                    size * sizeof(float)
                );

                py::buffer_info zem_buf_info = zem.request();
                float* zem_dest_ptr = static_cast<float*>(zem_buf_info.ptr);
                std::memcpy(
                    zem_dest_ptr,
                    zem_ptr,
                    size * sizeof(float)
                );

                // Package them into a list
                py::list result_list;
                result_list.append(pos);
                result_list.append(dir);
                result_list.append(wl);
                result_list.append(time);
                result_list.append(zem);

                // Return the views
                return result_list;
            },
            "Returns bunches as a list of NumPy array copy of photon positions, directions, "
            "wavelengths, arrival times and emission altitudes for a specific event to be passed to :py:meth:`iactsim.IACT.trace_photons` method.\n",
            py::arg("tel_id"),
            py::arg("event_index")
        );
    
    io_submodule.def(
        "read_file",
        &iactxx::read_file,
        R"raw(
            Read a file produced by CORSIKA IACT extension and return a :py:class:`IACTFile` 
            instance containing the photon bunches data ready to be passed to :py:meth:`iactsim.IACT.trace_photons`.

            Parameters
            ----------
            filepath : str
                Path of the CORSIKA file
            skip_telescopes : list[int]
                Telescope ID that can be skipped
            min_n_bunches : int
                Parse only events with more than `min_n_bunches` bunches
            
            Returns
            -------
            :py:class:`IACTFile`
                File handler
            
        )raw",
        py::arg("filepath"),
        py::arg("skip_telescopes")=std::vector<int>(),
        py::arg("min_n_bunches")=1,
        py::call_guard<py::gil_scoped_release>()
    );
    
    io_submodule.def(
        "read_files",
        &iactxx::read_files,
        R"raw(
            Read in parallel a list of files produced by CORSIKA IACT extension and return 
            the corresponding :py:class:`IACTFile` instances containing the photon bunches data
            ready to be passed to :py:meth:`iactsim.IACT.trace_photons`.

            Useful when multiple gzipped CORSIKA files have to be read.

            Parameters
            ----------
            filepaths : list[str]
                List of CORSIKA file paths
            skip_telescopes : list[int]
                Telescope ID that can be skipped
            min_n_bunches : int
                Parse only events with more than `min_n_bunches` bunches
            
            Returns
            -------
            list[:py:class:`IACTFile`]
                List of file handlers
            
        )raw",
        py::arg("filepaths"),
        py::arg("skip_telescopes")=std::vector<int>(),
        py::arg("min_n_bunches")=1,
        py::call_guard<py::gil_scoped_release>()
    );
}