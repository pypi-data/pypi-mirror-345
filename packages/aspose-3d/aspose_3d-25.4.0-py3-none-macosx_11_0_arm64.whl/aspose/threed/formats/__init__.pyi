from typing import List, Optional, Dict, Iterable, Any, overload
import io
import collections.abc
from collections.abc import Sequence
from datetime import datetime
from aspose.pyreflection import Type
import aspose.pycore
import aspose.pydrawing
from uuid import UUID
import aspose.threed
import aspose.threed.animation
import aspose.threed.deformers
import aspose.threed.entities
import aspose.threed.formats
import aspose.threed.formats.gltf
import aspose.threed.profiles
import aspose.threed.render
import aspose.threed.shading
import aspose.threed.utilities

class A3dwSaveOptions(SaveOptions):
    '''Save options for A3DW format.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.A3dwSaveOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def export_meta_data(self) -> bool:
        '''Export meta data associated with Scene/Node to client
        Default value is true'''
        raise NotImplementedError()
    
    @export_meta_data.setter
    def export_meta_data(self, value : bool) -> None:
        '''Export meta data associated with Scene/Node to client
        Default value is true'''
        raise NotImplementedError()
    
    @property
    def meta_data_prefix(self) -> str:
        '''If this property is non-null, only the properties of Scene/Node that start with this prefix will be exported, and the prefix will be removed.'''
        raise NotImplementedError()
    
    @meta_data_prefix.setter
    def meta_data_prefix(self, value : str) -> None:
        '''If this property is non-null, only the properties of Scene/Node that start with this prefix will be exported, and the prefix will be removed.'''
        raise NotImplementedError()
    

class AmfSaveOptions(SaveOptions):
    '''Save options for AMF'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.AmfSaveOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def enable_compression(self) -> bool:
        '''Whether to use compression to reduce the final file size, default value is true'''
        raise NotImplementedError()
    
    @enable_compression.setter
    def enable_compression(self, value : bool) -> None:
        '''Whether to use compression to reduce the final file size, default value is true'''
        raise NotImplementedError()
    

class ColladaSaveOptions(SaveOptions):
    '''Save options for collada'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.ColladaSaveOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def indented(self) -> bool:
        '''Gets whether the exported XML document is indented.'''
        raise NotImplementedError()
    
    @indented.setter
    def indented(self, value : bool) -> None:
        '''Sets whether the exported XML document is indented.'''
        raise NotImplementedError()
    
    @property
    def transform_style(self) -> aspose.threed.formats.ColladaTransformStyle:
        '''Gets the style of node transformation'''
        raise NotImplementedError()
    
    @transform_style.setter
    def transform_style(self, value : aspose.threed.formats.ColladaTransformStyle) -> None:
        '''Sets the style of node transformation'''
        raise NotImplementedError()
    

class Discreet3dsLoadOptions(LoadOptions):
    '''Load options for 3DS file.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.Discreet3dsLoadOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def gamma_corrected_color(self) -> bool:
        '''A 3ds file may contains original color and gamma corrected color for same attribute,
        Setting this to true will use the gamma corrected color if possible,
        otherwise the Aspose.3D will try to use the original color.'''
        raise NotImplementedError()
    
    @gamma_corrected_color.setter
    def gamma_corrected_color(self, value : bool) -> None:
        '''A 3ds file may contains original color and gamma corrected color for same attribute,
        Setting this to true will use the gamma corrected color if possible,
        otherwise the Aspose.3D will try to use the original color.'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate_system(self) -> bool:
        '''Gets flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    
    @flip_coordinate_system.setter
    def flip_coordinate_system(self, value : bool) -> None:
        '''Sets flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    
    @property
    def apply_animation_transform(self) -> bool:
        '''Gets whether to use the transformation defined in the first frame of animation track.'''
        raise NotImplementedError()
    
    @apply_animation_transform.setter
    def apply_animation_transform(self, value : bool) -> None:
        '''Sets whether to use the transformation defined in the first frame of animation track.'''
        raise NotImplementedError()
    

class Discreet3dsSaveOptions(SaveOptions):
    '''Save options for 3DS file.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.Discreet3dsSaveOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def export_light(self) -> bool:
        '''Gets whether export all lights in the scene.'''
        raise NotImplementedError()
    
    @export_light.setter
    def export_light(self, value : bool) -> None:
        '''Sets whether export all lights in the scene.'''
        raise NotImplementedError()
    
    @property
    def export_camera(self) -> bool:
        '''Gets whether export all cameras in the scene.'''
        raise NotImplementedError()
    
    @export_camera.setter
    def export_camera(self, value : bool) -> None:
        '''Sets whether export all cameras in the scene.'''
        raise NotImplementedError()
    
    @property
    def duplicated_name_separator(self) -> str:
        '''The separator between object\'s name and the duplicated counter, default value is "_".
        
        When scene contains objects that use the same name, Aspose.3D 3DS exporter will generate a different name for the object.
        For example there\'s two nodes named "Box", the first node will have a name "Box",
        and the second node will get a new name "Box_2" using the default configuration.'''
        raise NotImplementedError()
    
    @duplicated_name_separator.setter
    def duplicated_name_separator(self, value : str) -> None:
        '''The separator between object\'s name and the duplicated counter, default value is "_".
        
        When scene contains objects that use the same name, Aspose.3D 3DS exporter will generate a different name for the object.
        For example there\'s two nodes named "Box", the first node will have a name "Box",
        and the second node will get a new name "Box_2" using the default configuration.'''
        raise NotImplementedError()
    
    @property
    def duplicated_name_counter_base(self) -> int:
        '''The counter used by generating new name for duplicated names, default value is 2.'''
        raise NotImplementedError()
    
    @duplicated_name_counter_base.setter
    def duplicated_name_counter_base(self, value : int) -> None:
        '''The counter used by generating new name for duplicated names, default value is 2.'''
        raise NotImplementedError()
    
    @property
    def duplicated_name_counter_format(self) -> str:
        '''The format of the duplicated counter, default value is empty string.'''
        raise NotImplementedError()
    
    @duplicated_name_counter_format.setter
    def duplicated_name_counter_format(self, value : str) -> None:
        '''The format of the duplicated counter, default value is empty string.'''
        raise NotImplementedError()
    
    @property
    def master_scale(self) -> float:
        '''Gets the master scale used in exporting.'''
        raise NotImplementedError()
    
    @master_scale.setter
    def master_scale(self, value : float) -> None:
        '''Sets the master scale used in exporting.'''
        raise NotImplementedError()
    
    @property
    def gamma_corrected_color(self) -> bool:
        '''A 3ds file may contains original color and gamma corrected color for same attribute,
        Setting this to true will use the gamma corrected color if possible,
        otherwise the Aspose.3D will try to use the original color.'''
        raise NotImplementedError()
    
    @gamma_corrected_color.setter
    def gamma_corrected_color(self, value : bool) -> None:
        '''A 3ds file may contains original color and gamma corrected color for same attribute,
        Setting this to true will use the gamma corrected color if possible,
        otherwise the Aspose.3D will try to use the original color.'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate_system(self) -> bool:
        '''Gets flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    
    @flip_coordinate_system.setter
    def flip_coordinate_system(self, value : bool) -> None:
        '''Sets flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    
    @property
    def high_precise_color(self) -> bool:
        '''If this is true, the generated 3ds file will use high precise color, means each channel of red/green/blue are in 32bit float.
        Otherwise the generated file will use 24bit color, each channel use 8bit byte.
        The default value is false, because not all applications supports the high-precise color.'''
        raise NotImplementedError()
    
    @high_precise_color.setter
    def high_precise_color(self, value : bool) -> None:
        '''If this is true, the generated 3ds file will use high precise color, means each channel of red/green/blue are in 32bit float.
        Otherwise the generated file will use 24bit color, each channel use 8bit byte.
        The default value is false, because not all applications supports the high-precise color.'''
        raise NotImplementedError()
    

class DracoFormat(aspose.threed.FileFormat):
    '''Google Draco format'''
    
    @overload
    @staticmethod
    def detect(stream : io._IOBase, file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from data stream, file name is optional for guessing types that has no magic header.
        
        :param stream: Stream containing data to detect
        :param file_name: Original file name of the data, used as hint.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def detect(file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from file name, file must be readable so Aspose.3D can detect the file format through file header.
        
        :param file_name: Path to the file to detect file format.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @overload
    def decode(self, file_name : str) -> aspose.threed.entities.Geometry:
        '''Decode the point cloud or mesh from specified file name
        
        :param file_name: The file name contains the drc file
        :returns: A :py:class:`aspose.threed.entities.Mesh` or :py:class:`aspose.threed.entities.PointCloud` instance depends on the file content'''
        raise NotImplementedError()
    
    @overload
    def decode(self, data : List[int]) -> aspose.threed.entities.Geometry:
        '''Decode the point cloud or mesh from memory data
        
        :param data: The raw drc bytes
        :returns: A :py:class:`aspose.threed.entities.Mesh` or :py:class:`aspose.threed.entities.PointCloud` instance depends on the content'''
        raise NotImplementedError()
    
    @overload
    def encode(self, entity : aspose.threed.Entity, stream : io._IOBase, options : aspose.threed.formats.DracoSaveOptions) -> None:
        '''Encode the entity to specified stream
        
        :param entity: The entity to be encoded
        :param stream: The stream that encoded data will be written to
        :param options: Extra options for encoding the point cloud'''
        raise NotImplementedError()
    
    @overload
    def encode(self, entity : aspose.threed.Entity, file_name : str, options : aspose.threed.formats.DracoSaveOptions) -> None:
        '''Encode the entity to specified file
        
        :param entity: The entity to be encoded
        :param file_name: The file name to be written
        :param options: Extra options for encoding the point cloud'''
        raise NotImplementedError()
    
    @overload
    def encode(self, entity : aspose.threed.Entity, options : aspose.threed.formats.DracoSaveOptions) -> List[int]:
        '''Encode the entity to Draco raw data
        
        :param entity: The entity to be encoded
        :param options: Extra options for encoding the point cloud
        :returns: The encoded draco data represented in bytes'''
        raise NotImplementedError()
    
    @staticmethod
    def get_format_by_extension(extension_name : str) -> aspose.threed.FileFormat:
        '''Gets the preferred file format from the file extension name
        The extension name should starts with a dot(\'.\').
        
        :param extension_name: The extension name started with \'.\' to query.
        :returns: Instance of :py:class:`aspose.threed.FileFormat`, otherwise null returned.'''
        raise NotImplementedError()
    
    def create_load_options(self) -> aspose.threed.formats.LoadOptions:
        '''Create a default load options for this file format
        
        :returns: A default load option for current format'''
        raise NotImplementedError()
    
    def create_save_options(self) -> aspose.threed.formats.SaveOptions:
        '''Create a default save options for this file format
        
        :returns: A default save option for current format'''
        raise NotImplementedError()
    
    @property
    def formats(self) -> List[aspose.threed.FileFormat]:
        '''Access to all supported formats'''
        raise NotImplementedError()

    @property
    def version(self) -> tuple[int, int]:
        '''Gets file format version'''
        raise NotImplementedError()
    
    @property
    def can_export(self) -> bool:
        '''Gets whether Aspose.3D supports export scene to current file format.'''
        raise NotImplementedError()
    
    @property
    def can_import(self) -> bool:
        '''Gets whether Aspose.3D supports import scene from current file format.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''Gets the extension name of this type.'''
        raise NotImplementedError()
    
    @property
    def extensions(self) -> List[str]:
        '''Gets the extension names of this type.'''
        raise NotImplementedError()
    
    @property
    def content_type(self) -> aspose.threed.FileContentType:
        '''Gets file format content type'''
        raise NotImplementedError()
    
    @property
    def file_format_type(self) -> aspose.threed.FileFormatType:
        '''Gets file format type'''
        raise NotImplementedError()
    
    @property
    def FBX6100ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX6100_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def MAYA_ASCII(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in ASCII format'''
        raise NotImplementedError()

    @property
    def MAYA_BINARY(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in Binary format'''
        raise NotImplementedError()

    @property
    def STL_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary STL file format'''
        raise NotImplementedError()

    @property
    def STLASCII(self) -> aspose.threed.FileFormat:
        '''ASCII STL file format'''
        raise NotImplementedError()

    @property
    def WAVEFRONT_OBJ(self) -> aspose.threed.FileFormat:
        '''Wavefront\'s Obj file format'''
        raise NotImplementedError()

    @property
    def DISCREET_3DS(self) -> aspose.threed.FileFormat:
        '''3D Studio\'s file format'''
        raise NotImplementedError()

    @property
    def COLLADA(self) -> aspose.threed.FileFormat:
        '''Collada file format'''
        raise NotImplementedError()

    @property
    def UNIVERSAL_3D(self) -> aspose.threed.FileFormat:
        '''Universal3D file format'''
        raise NotImplementedError()

    @property
    def GLTF(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF'''
        raise NotImplementedError()

    @property
    def GLTF2(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def GLTF_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF in Binary format'''
        raise NotImplementedError()

    @property
    def GLTF2_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def PDF(self) -> aspose.threed.formats.PdfFormat:
        '''Adobe\'s Portable Document Format'''
        raise NotImplementedError()

    @property
    def BLENDER(self) -> aspose.threed.FileFormat:
        '''Blender\'s 3D file format'''
        raise NotImplementedError()

    @property
    def DXF(self) -> aspose.threed.FileFormat:
        '''AutoCAD DXF'''
        raise NotImplementedError()

    @property
    def PLY(self) -> aspose.threed.formats.PlyFormat:
        '''Polygon File Format or Stanford Triangle Format'''
        raise NotImplementedError()

    @property
    def X_BINARY(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def X_TEXT(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def DRACO(self) -> aspose.threed.formats.DracoFormat:
        '''Google Draco Mesh'''
        raise NotImplementedError()

    @property
    def MICROSOFT_3MF(self) -> aspose.threed.formats.Microsoft3MFFormat:
        '''Microsoft 3D Manufacturing Format'''
        raise NotImplementedError()

    @property
    def RVM_TEXT(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in text format'''
        raise NotImplementedError()

    @property
    def RVM_BINARY(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in binary format'''
        raise NotImplementedError()

    @property
    def ASE(self) -> aspose.threed.FileFormat:
        '''3D Studio Max\'s ASCII Scene Exporter format.'''
        raise NotImplementedError()

    @property
    def IFC(self) -> aspose.threed.FileFormat:
        '''ISO 16739-1 Industry Foundation Classes data model.'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT8(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 8'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT9(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 9'''
        raise NotImplementedError()

    @property
    def AMF(self) -> aspose.threed.FileFormat:
        '''Additive manufacturing file format'''
        raise NotImplementedError()

    @property
    def VRML(self) -> aspose.threed.FileFormat:
        '''The Virtual Reality Modeling Language'''
        raise NotImplementedError()

    @property
    def ASPOSE_3D_WEB(self) -> aspose.threed.FileFormat:
        '''Aspose.3D Web format.'''
        raise NotImplementedError()

    @property
    def HTML5(self) -> aspose.threed.FileFormat:
        '''HTML5 File'''
        raise NotImplementedError()

    @property
    def ZIP(self) -> aspose.threed.FileFormat:
        '''Zip archive that contains other 3d file format.'''
        raise NotImplementedError()

    @property
    def USD(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description'''
        raise NotImplementedError()

    @property
    def USDA(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description in ASCII format.'''
        raise NotImplementedError()

    @property
    def USDZ(self) -> aspose.threed.FileFormat:
        '''Compressed Universal Scene Description'''
        raise NotImplementedError()

    @property
    def XYZ(self) -> aspose.threed.FileFormat:
        '''Xyz point cloud file'''
        raise NotImplementedError()

    @property
    def PCD(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in ASCII mode'''
        raise NotImplementedError()

    @property
    def PCD_BINARY(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in Binary mode'''
        raise NotImplementedError()


class DracoSaveOptions(SaveOptions):
    '''Save options for Google draco files'''
    
    def __init__(self) -> None:
        '''Construct a default configuration for saving draco files.'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def position_bits(self) -> int:
        '''Quantization bits for position, default value is 14'''
        raise NotImplementedError()
    
    @position_bits.setter
    def position_bits(self, value : int) -> None:
        '''Quantization bits for position, default value is 14'''
        raise NotImplementedError()
    
    @property
    def texture_coordinate_bits(self) -> int:
        '''Quantization bits for texture coordinate, default value is 12'''
        raise NotImplementedError()
    
    @texture_coordinate_bits.setter
    def texture_coordinate_bits(self, value : int) -> None:
        '''Quantization bits for texture coordinate, default value is 12'''
        raise NotImplementedError()
    
    @property
    def color_bits(self) -> int:
        '''Quantization bits for vertex color, default value is 10'''
        raise NotImplementedError()
    
    @color_bits.setter
    def color_bits(self, value : int) -> None:
        '''Quantization bits for vertex color, default value is 10'''
        raise NotImplementedError()
    
    @property
    def normal_bits(self) -> int:
        '''Quantization bits for normal vectors, default value is 10'''
        raise NotImplementedError()
    
    @normal_bits.setter
    def normal_bits(self, value : int) -> None:
        '''Quantization bits for normal vectors, default value is 10'''
        raise NotImplementedError()
    
    @property
    def compression_level(self) -> aspose.threed.formats.DracoCompressionLevel:
        '''Compression level, default value is :py:attr:`aspose.threed.formats.DracoCompressionLevel.STANDARD`'''
        raise NotImplementedError()
    
    @compression_level.setter
    def compression_level(self, value : aspose.threed.formats.DracoCompressionLevel) -> None:
        '''Compression level, default value is :py:attr:`aspose.threed.formats.DracoCompressionLevel.STANDARD`'''
        raise NotImplementedError()
    
    @property
    def apply_unit_scale(self) -> bool:
        '''Apply :py:attr:`aspose.threed.AssetInfo.unit_scale_factor` to the mesh.
        Default value is false.'''
        raise NotImplementedError()
    
    @apply_unit_scale.setter
    def apply_unit_scale(self, value : bool) -> None:
        '''Apply :py:attr:`aspose.threed.AssetInfo.unit_scale_factor` to the mesh.
        Default value is false.'''
        raise NotImplementedError()
    
    @property
    def point_cloud(self) -> bool:
        '''Export the scene as point cloud, default value is false.'''
        raise NotImplementedError()
    
    @point_cloud.setter
    def point_cloud(self, value : bool) -> None:
        '''Export the scene as point cloud, default value is false.'''
        raise NotImplementedError()
    

class FbxLoadOptions(LoadOptions):
    '''Load options for Fbx format.'''
    
    @overload
    def __init__(self, format : aspose.threed.FileFormat) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.FbxLoadOptions`
        
        :param format: Instance of :py:class:`aspose.threed.FileFormat`, it should be a valid FBX format.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.FbxLoadOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def keep_builtin_global_settings(self) -> bool:
        '''Gets whether to keep the builtin properties in GlobalSettings which have a native property replacement in :py:class:`aspose.threed.AssetInfo`.
        Set this to true if you want the full properties in GlobalSettings
        Default value is false'''
        raise NotImplementedError()
    
    @keep_builtin_global_settings.setter
    def keep_builtin_global_settings(self, value : bool) -> None:
        '''Sets whether to keep the builtin properties in GlobalSettings which have a native property replacement in :py:class:`aspose.threed.AssetInfo`.
        Set this to true if you want the full properties in GlobalSettings
        Default value is false'''
        raise NotImplementedError()
    
    @property
    def compatible_mode(self) -> bool:
        '''Gets whether to enable compatible mode.
        Compatible mode will try to support non-standard FBX definitions like PBR materials exported by Blender.
        Default value is false.'''
        raise NotImplementedError()
    
    @compatible_mode.setter
    def compatible_mode(self, value : bool) -> None:
        '''Sets whether to enable compatible mode.
        Compatible mode will try to support non-standard FBX definitions like PBR materials exported by Blender.
        Default value is false.'''
        raise NotImplementedError()
    

class FbxSaveOptions(SaveOptions):
    '''Save options for Fbx file.'''
    
    @overload
    def __init__(self, format : aspose.threed.FileFormat) -> None:
        '''Initializes a :py:class:`aspose.threed.formats.FbxSaveOptions`
        
        :param format: Instance of :py:class:`aspose.threed.FileFormat`, it should be a valid FBX format.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, content_type : aspose.threed.FileContentType) -> None:
        '''Initialize a :py:class:`aspose.threed.formats.FbxSaveOptions` using latest supported version.
        
        :param content_type: Binary or ASCII'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def reuse_primitive_mesh(self) -> bool:
        '''Reuse the mesh for the primitives with same parameters, this will significantly reduce the size of FBX output which scene was constructed by large set of primitive shapes(like imported from CAD files).
        Default value is false'''
        raise NotImplementedError()
    
    @reuse_primitive_mesh.setter
    def reuse_primitive_mesh(self, value : bool) -> None:
        '''Reuse the mesh for the primitives with same parameters, this will significantly reduce the size of FBX output which scene was constructed by large set of primitive shapes(like imported from CAD files).
        Default value is false'''
        raise NotImplementedError()
    
    @property
    def enable_compression(self) -> bool:
        '''Compression large binary data in the FBX file(e.g. animation data, control points, vertex element data, indices), default value is true.'''
        raise NotImplementedError()
    
    @enable_compression.setter
    def enable_compression(self, value : bool) -> None:
        '''Compression large binary data in the FBX file(e.g. animation data, control points, vertex element data, indices), default value is true.'''
        raise NotImplementedError()
    
    @property
    def fold_repeated_curve_data(self) -> Optional[bool]:
        '''Gets whether reuse repeated curve data by increasing last data\'s ref count'''
        raise NotImplementedError()
    
    @fold_repeated_curve_data.setter
    def fold_repeated_curve_data(self, value : Optional[bool]) -> None:
        '''Sets whether reuse repeated curve data by increasing last data\'s ref count'''
        raise NotImplementedError()
    
    @property
    def export_legacy_material_properties(self) -> bool:
        '''Gets whether export legacy material properties, used for back compatibility.
        This option is turned on by default.'''
        raise NotImplementedError()
    
    @export_legacy_material_properties.setter
    def export_legacy_material_properties(self, value : bool) -> None:
        '''Sets whether export legacy material properties, used for back compatibility.
        This option is turned on by default.'''
        raise NotImplementedError()
    
    @property
    def video_for_texture(self) -> bool:
        '''Gets whether generate a Video instance for :py:class:`aspose.threed.shading.Texture` when exporting as FBX.'''
        raise NotImplementedError()
    
    @video_for_texture.setter
    def video_for_texture(self, value : bool) -> None:
        '''Sets whether generate a Video instance for :py:class:`aspose.threed.shading.Texture` when exporting as FBX.'''
        raise NotImplementedError()
    
    @property
    def embed_textures(self) -> bool:
        '''Gets whether to embed the texture to the final output file.
        FBX Exporter will try to find the texture\'s raw data from :py:attr:`aspose.threed.formats.IOConfig.file_system`, and embed the file to final FBX file.
        Default value is false.'''
        raise NotImplementedError()
    
    @embed_textures.setter
    def embed_textures(self, value : bool) -> None:
        '''Sets whether to embed the texture to the final output file.
        FBX Exporter will try to find the texture\'s raw data from :py:attr:`aspose.threed.formats.IOConfig.file_system`, and embed the file to final FBX file.
        Default value is false.'''
        raise NotImplementedError()
    
    @property
    def generate_vertex_element_material(self) -> bool:
        '''Gets whether always generate a :py:class:`aspose.threed.entities.VertexElementMaterial` for geometries if the attached node contains materials.
        This is turned off by default.'''
        raise NotImplementedError()
    
    @generate_vertex_element_material.setter
    def generate_vertex_element_material(self, value : bool) -> None:
        '''Sets whether always generate a :py:class:`aspose.threed.entities.VertexElementMaterial` for geometries if the attached node contains materials.
        This is turned off by default.'''
        raise NotImplementedError()
    

class GltfLoadOptions(LoadOptions):
    '''Load options for glTF format'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.GltfLoadOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def flip_tex_coord_v(self) -> bool:
        '''Flip the v(t) coordinate in mesh\'s texture coordinate, default value is true.'''
        raise NotImplementedError()
    
    @flip_tex_coord_v.setter
    def flip_tex_coord_v(self, value : bool) -> None:
        '''Flip the v(t) coordinate in mesh\'s texture coordinate, default value is true.'''
        raise NotImplementedError()
    

class GltfSaveOptions(SaveOptions):
    '''Save options for glTF format.'''
    
    @overload
    def __init__(self, content_type : aspose.threed.FileContentType) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.GltfSaveOptions`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, format : aspose.threed.FileFormat) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.GltfSaveOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def pretty_print(self) -> bool:
        '''The JSON content of GLTF file is indented for human reading, default value is false'''
        raise NotImplementedError()
    
    @pretty_print.setter
    def pretty_print(self, value : bool) -> None:
        '''The JSON content of GLTF file is indented for human reading, default value is false'''
        raise NotImplementedError()
    
    @property
    def fallback_normal(self) -> Optional[aspose.threed.utilities.Vector3]:
        '''When GLTF2 exporter detected an invalid normal, this will be used instead of its original value to bypass the validation.
        Default value is (0, 1, 0)'''
        raise NotImplementedError()
    
    @fallback_normal.setter
    def fallback_normal(self, value : Optional[aspose.threed.utilities.Vector3]) -> None:
        '''When GLTF2 exporter detected an invalid normal, this will be used instead of its original value to bypass the validation.
        Default value is (0, 1, 0)'''
        raise NotImplementedError()
    
    @property
    def embed_assets(self) -> bool:
        '''Embed all external assets as base64 into single file in ASCII mode, default value is false.'''
        raise NotImplementedError()
    
    @embed_assets.setter
    def embed_assets(self, value : bool) -> None:
        '''Embed all external assets as base64 into single file in ASCII mode, default value is false.'''
        raise NotImplementedError()
    
    @property
    def image_format(self) -> aspose.threed.formats.GltfEmbeddedImageFormat:
        '''Standard glTF only supports PNG/JPG as its texture format, this option will guide how Aspose.3D
        convert the non-standard images to supported format during the exporting.
        Default value is :py:attr:`aspose.threed.formats.GltfEmbeddedImageFormat.PNG`'''
        raise NotImplementedError()
    
    @image_format.setter
    def image_format(self, value : aspose.threed.formats.GltfEmbeddedImageFormat) -> None:
        '''Standard glTF only supports PNG/JPG as its texture format, this option will guide how Aspose.3D
        convert the non-standard images to supported format during the exporting.
        Default value is :py:attr:`aspose.threed.formats.GltfEmbeddedImageFormat.PNG`'''
        raise NotImplementedError()
    
    @property
    def use_common_materials(self) -> bool:
        '''Serialize materials using KHR common material extensions, default value is false.
        Set this to false will cause Aspose.3D export a set of vertex/fragment shader if :py:attr:`aspose.threed.formats.GltfSaveOptions.ExportShaders`'''
        raise NotImplementedError()
    
    @use_common_materials.setter
    def use_common_materials(self, value : bool) -> None:
        '''Serialize materials using KHR common material extensions, default value is false.
        Set this to false will cause Aspose.3D export a set of vertex/fragment shader if :py:attr:`aspose.threed.formats.GltfSaveOptions.ExportShaders`'''
        raise NotImplementedError()
    
    @property
    def external_draco_encoder(self) -> str:
        '''Use external draco encoder to accelerate the draco compression speed.'''
        raise NotImplementedError()
    
    @external_draco_encoder.setter
    def external_draco_encoder(self, value : str) -> None:
        '''Use external draco encoder to accelerate the draco compression speed.'''
        raise NotImplementedError()
    
    @property
    def flip_tex_coord_v(self) -> bool:
        '''Flip texture coordinate  v(t) component, default value is true.'''
        raise NotImplementedError()
    
    @flip_tex_coord_v.setter
    def flip_tex_coord_v(self, value : bool) -> None:
        '''Flip texture coordinate  v(t) component, default value is true.'''
        raise NotImplementedError()
    
    @property
    def buffer_file(self) -> str:
        '''The file name of the external buffer file used to store binary data.
        If this file is not specified, Aspose.3D will generate a name for you.
        This is ignored when export glTF in binary mode.'''
        raise NotImplementedError()
    
    @buffer_file.setter
    def buffer_file(self, value : str) -> None:
        '''The file name of the external buffer file used to store binary data.
        If this file is not specified, Aspose.3D will generate a name for you.
        This is ignored when export glTF in binary mode.'''
        raise NotImplementedError()
    
    @property
    def save_extras(self) -> bool:
        '''Save scene object\'s dynamic properties into \'extra\' fields in the generated glTF file.
        This is useful to provide application-specific data.
        Default value is false.'''
        raise NotImplementedError()
    
    @save_extras.setter
    def save_extras(self, value : bool) -> None:
        '''Save scene object\'s dynamic properties into \'extra\' fields in the generated glTF file.
        This is useful to provide application-specific data.
        Default value is false.'''
        raise NotImplementedError()
    
    @property
    def apply_unit_scale(self) -> bool:
        '''Apply :py:attr:`aspose.threed.AssetInfo.unit_scale_factor` to the mesh.
        Default value is false.'''
        raise NotImplementedError()
    
    @apply_unit_scale.setter
    def apply_unit_scale(self, value : bool) -> None:
        '''Apply :py:attr:`aspose.threed.AssetInfo.unit_scale_factor` to the mesh.
        Default value is false.'''
        raise NotImplementedError()
    
    @property
    def draco_compression(self) -> bool:
        '''Gets whether to enable draco compression'''
        raise NotImplementedError()
    
    @draco_compression.setter
    def draco_compression(self, value : bool) -> None:
        '''Sets whether to enable draco compression'''
        raise NotImplementedError()
    

class Html5SaveOptions(SaveOptions):
    '''Save options for HTML5'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.Html5SaveOptions` with all default settings.'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def show_grid(self) -> bool:
        '''Display a grid in the scene.
        Default value is true.'''
        raise NotImplementedError()
    
    @show_grid.setter
    def show_grid(self, value : bool) -> None:
        '''Display a grid in the scene.
        Default value is true.'''
        raise NotImplementedError()
    
    @property
    def show_rulers(self) -> bool:
        '''Display rulers of x/y/z axes in the scene to measure the model.
        Default value is false.'''
        raise NotImplementedError()
    
    @show_rulers.setter
    def show_rulers(self, value : bool) -> None:
        '''Display rulers of x/y/z axes in the scene to measure the model.
        Default value is false.'''
        raise NotImplementedError()
    
    @property
    def show_ui(self) -> bool:
        '''Display a simple UI in the scene.
        Default value is true.'''
        raise NotImplementedError()
    
    @show_ui.setter
    def show_ui(self, value : bool) -> None:
        '''Display a simple UI in the scene.
        Default value is true.'''
        raise NotImplementedError()
    
    @property
    def orientation_box(self) -> bool:
        '''Display a orientation box.
        Default value is true.'''
        raise NotImplementedError()
    
    @orientation_box.setter
    def orientation_box(self, value : bool) -> None:
        '''Display a orientation box.
        Default value is true.'''
        raise NotImplementedError()
    
    @property
    def up_vector(self) -> str:
        '''Gets the up vector, value can be "x"/"y"/"z", default value is "y"'''
        raise NotImplementedError()
    
    @up_vector.setter
    def up_vector(self, value : str) -> None:
        '''Sets the up vector, value can be "x"/"y"/"z", default value is "y"'''
        raise NotImplementedError()
    
    @property
    def far_plane(self) -> float:
        '''Gets the far plane of the camera, default value is 1000.'''
        raise NotImplementedError()
    
    @far_plane.setter
    def far_plane(self, value : float) -> None:
        '''Sets the far plane of the camera, default value is 1000.'''
        raise NotImplementedError()
    
    @property
    def near_plane(self) -> float:
        '''Gets the near plane of the camera, default value is 1'''
        raise NotImplementedError()
    
    @near_plane.setter
    def near_plane(self, value : float) -> None:
        '''Sets the near plane of the camera, default value is 1'''
        raise NotImplementedError()
    
    @property
    def look_at(self) -> aspose.threed.utilities.Vector3:
        '''Gets the default look at position, default value is (0, 0, 0)'''
        raise NotImplementedError()
    
    @look_at.setter
    def look_at(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the default look at position, default value is (0, 0, 0)'''
        raise NotImplementedError()
    
    @property
    def camera_position(self) -> aspose.threed.utilities.Vector3:
        '''Gets the initial position of the camera, default value is (10, 10, 10)'''
        raise NotImplementedError()
    
    @camera_position.setter
    def camera_position(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the initial position of the camera, default value is (10, 10, 10)'''
        raise NotImplementedError()
    
    @property
    def field_of_view(self) -> float:
        '''Gets the field of the view, default value is 45, measured in degree.'''
        raise NotImplementedError()
    
    @field_of_view.setter
    def field_of_view(self, value : float) -> None:
        '''Sets the field of the view, default value is 45, measured in degree.'''
        raise NotImplementedError()
    

class IOConfig:
    '''IO config for serialization/deserialization.
    User can specify detailed configurations like dependency look-up path
    Or format-related configs here'''
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    

class JtLoadOptions(LoadOptions):
    '''Load options for Siemens JT'''
    
    def __init__(self) -> None:
        ''''''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def load_properties(self) -> bool:
        '''Load properties from JT\'s property table as Aspose.3D properties.
        Default value is false.'''
        raise NotImplementedError()
    
    @load_properties.setter
    def load_properties(self, value : bool) -> None:
        '''Load properties from JT\'s property table as Aspose.3D properties.
        Default value is false.'''
        raise NotImplementedError()
    
    @property
    def load_pmi(self) -> bool:
        '''Load PMI information from JT file if possible, the data will be saved as property "PMI" of :py:attr:`aspose.threed.Scene.asset_info`.
        Default value is false.'''
        raise NotImplementedError()
    
    @load_pmi.setter
    def load_pmi(self, value : bool) -> None:
        '''Load PMI information from JT file if possible, the data will be saved as property "PMI" of :py:attr:`aspose.threed.Scene.asset_info`.
        Default value is false.'''
        raise NotImplementedError()
    

class LoadOptions(IOConfig):
    '''The base class to configure options in file loading for different types'''
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    

class Microsoft3MFFormat(aspose.threed.FileFormat):
    '''File format instance for Microsoft 3MF with 3MF related utilities.'''
    
    @overload
    @staticmethod
    def detect(stream : io._IOBase, file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from data stream, file name is optional for guessing types that has no magic header.
        
        :param stream: Stream containing data to detect
        :param file_name: Original file name of the data, used as hint.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def detect(file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from file name, file must be readable so Aspose.3D can detect the file format through file header.
        
        :param file_name: Path to the file to detect file format.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @staticmethod
    def get_format_by_extension(extension_name : str) -> aspose.threed.FileFormat:
        '''Gets the preferred file format from the file extension name
        The extension name should starts with a dot(\'.\').
        
        :param extension_name: The extension name started with \'.\' to query.
        :returns: Instance of :py:class:`aspose.threed.FileFormat`, otherwise null returned.'''
        raise NotImplementedError()
    
    def create_load_options(self) -> aspose.threed.formats.LoadOptions:
        '''Create a default load options for this file format
        
        :returns: A default load option for current format'''
        raise NotImplementedError()
    
    def create_save_options(self) -> aspose.threed.formats.SaveOptions:
        '''Create a default save options for this file format
        
        :returns: A default save option for current format'''
        raise NotImplementedError()
    
    def is_buildable(self, node : aspose.threed.Node) -> bool:
        '''Check if this node is marked as a build.
        
        :param node: Which node to check
        :returns: True if it\'s marked as a build'''
        raise NotImplementedError()
    
    def get_transform_for_build(self, node : aspose.threed.Node) -> Optional[aspose.threed.utilities.Matrix4]:
        '''Get transform matrix for node used in build.
        
        :param node: Which node to get transform matrix for 3MF build.
        :returns: A transform matrix or null if not defined.'''
        raise NotImplementedError()
    
    def set_buildable(self, node : aspose.threed.Node, value : bool, transform : Optional[aspose.threed.utilities.Matrix4]) -> None:
        raise NotImplementedError()
    
    def set_object_type(self, node : aspose.threed.Node, model_type : str) -> None:
        '''Set the model type for specified node.
        Possible value:
        model
        surface
        solidsupport
        support
        other'''
        raise NotImplementedError()
    
    def get_object_type(self, node : aspose.threed.Node) -> str:
        '''Gets the model type for specified node.
        
        :returns: 3MF\'s object type for given node'''
        raise NotImplementedError()
    
    @property
    def formats(self) -> List[aspose.threed.FileFormat]:
        '''Access to all supported formats'''
        raise NotImplementedError()

    @property
    def version(self) -> tuple[int, int]:
        '''Gets file format version'''
        raise NotImplementedError()
    
    @property
    def can_export(self) -> bool:
        '''Gets whether Aspose.3D supports export scene to current file format.'''
        raise NotImplementedError()
    
    @property
    def can_import(self) -> bool:
        '''Gets whether Aspose.3D supports import scene from current file format.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''Gets the extension name of this type.'''
        raise NotImplementedError()
    
    @property
    def extensions(self) -> List[str]:
        '''Gets the extension names of this type.'''
        raise NotImplementedError()
    
    @property
    def content_type(self) -> aspose.threed.FileContentType:
        '''Gets file format content type'''
        raise NotImplementedError()
    
    @property
    def file_format_type(self) -> aspose.threed.FileFormatType:
        '''Gets file format type'''
        raise NotImplementedError()
    
    @property
    def FBX6100ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX6100_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def MAYA_ASCII(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in ASCII format'''
        raise NotImplementedError()

    @property
    def MAYA_BINARY(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in Binary format'''
        raise NotImplementedError()

    @property
    def STL_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary STL file format'''
        raise NotImplementedError()

    @property
    def STLASCII(self) -> aspose.threed.FileFormat:
        '''ASCII STL file format'''
        raise NotImplementedError()

    @property
    def WAVEFRONT_OBJ(self) -> aspose.threed.FileFormat:
        '''Wavefront\'s Obj file format'''
        raise NotImplementedError()

    @property
    def DISCREET_3DS(self) -> aspose.threed.FileFormat:
        '''3D Studio\'s file format'''
        raise NotImplementedError()

    @property
    def COLLADA(self) -> aspose.threed.FileFormat:
        '''Collada file format'''
        raise NotImplementedError()

    @property
    def UNIVERSAL_3D(self) -> aspose.threed.FileFormat:
        '''Universal3D file format'''
        raise NotImplementedError()

    @property
    def GLTF(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF'''
        raise NotImplementedError()

    @property
    def GLTF2(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def GLTF_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF in Binary format'''
        raise NotImplementedError()

    @property
    def GLTF2_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def PDF(self) -> aspose.threed.formats.PdfFormat:
        '''Adobe\'s Portable Document Format'''
        raise NotImplementedError()

    @property
    def BLENDER(self) -> aspose.threed.FileFormat:
        '''Blender\'s 3D file format'''
        raise NotImplementedError()

    @property
    def DXF(self) -> aspose.threed.FileFormat:
        '''AutoCAD DXF'''
        raise NotImplementedError()

    @property
    def PLY(self) -> aspose.threed.formats.PlyFormat:
        '''Polygon File Format or Stanford Triangle Format'''
        raise NotImplementedError()

    @property
    def X_BINARY(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def X_TEXT(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def DRACO(self) -> aspose.threed.formats.DracoFormat:
        '''Google Draco Mesh'''
        raise NotImplementedError()

    @property
    def MICROSOFT_3MF(self) -> aspose.threed.formats.Microsoft3MFFormat:
        '''Microsoft 3D Manufacturing Format'''
        raise NotImplementedError()

    @property
    def RVM_TEXT(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in text format'''
        raise NotImplementedError()

    @property
    def RVM_BINARY(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in binary format'''
        raise NotImplementedError()

    @property
    def ASE(self) -> aspose.threed.FileFormat:
        '''3D Studio Max\'s ASCII Scene Exporter format.'''
        raise NotImplementedError()

    @property
    def IFC(self) -> aspose.threed.FileFormat:
        '''ISO 16739-1 Industry Foundation Classes data model.'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT8(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 8'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT9(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 9'''
        raise NotImplementedError()

    @property
    def AMF(self) -> aspose.threed.FileFormat:
        '''Additive manufacturing file format'''
        raise NotImplementedError()

    @property
    def VRML(self) -> aspose.threed.FileFormat:
        '''The Virtual Reality Modeling Language'''
        raise NotImplementedError()

    @property
    def ASPOSE_3D_WEB(self) -> aspose.threed.FileFormat:
        '''Aspose.3D Web format.'''
        raise NotImplementedError()

    @property
    def HTML5(self) -> aspose.threed.FileFormat:
        '''HTML5 File'''
        raise NotImplementedError()

    @property
    def ZIP(self) -> aspose.threed.FileFormat:
        '''Zip archive that contains other 3d file format.'''
        raise NotImplementedError()

    @property
    def USD(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description'''
        raise NotImplementedError()

    @property
    def USDA(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description in ASCII format.'''
        raise NotImplementedError()

    @property
    def USDZ(self) -> aspose.threed.FileFormat:
        '''Compressed Universal Scene Description'''
        raise NotImplementedError()

    @property
    def XYZ(self) -> aspose.threed.FileFormat:
        '''Xyz point cloud file'''
        raise NotImplementedError()

    @property
    def PCD(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in ASCII mode'''
        raise NotImplementedError()

    @property
    def PCD_BINARY(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in Binary mode'''
        raise NotImplementedError()


class Microsoft3MFSaveOptions(SaveOptions):
    '''Save options for Microsoft 3MF file.'''
    
    def __init__(self) -> None:
        '''Construct a :py:class:`aspose.threed.formats.Microsoft3MFSaveOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def enable_compression(self) -> bool:
        '''Enable compression on the output 3mf file
        Default value is true'''
        raise NotImplementedError()
    
    @enable_compression.setter
    def enable_compression(self, value : bool) -> None:
        '''Enable compression on the output 3mf file
        Default value is true'''
        raise NotImplementedError()
    
    @property
    def build_all(self) -> bool:
        '''Mark all geometries in scene to be printable.
        Or you can manually mark node to be printable by :py:func:`aspose.threed.formats.Microsoft3MFFormat.set_buildable`
        Default value is true'''
        raise NotImplementedError()
    
    @build_all.setter
    def build_all(self, value : bool) -> None:
        '''Mark all geometries in scene to be printable.
        Or you can manually mark node to be printable by :py:func:`aspose.threed.formats.Microsoft3MFFormat.set_buildable`
        Default value is true'''
        raise NotImplementedError()
    

class ObjLoadOptions(LoadOptions):
    '''Load options for wavefront obj'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.ObjLoadOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate_system(self) -> bool:
        '''Gets whether flip coordinate system of control points/normal during importing'''
        raise NotImplementedError()
    
    @flip_coordinate_system.setter
    def flip_coordinate_system(self, value : bool) -> None:
        '''Sets whether flip coordinate system of control points/normal during importing'''
        raise NotImplementedError()
    
    @property
    def enable_materials(self) -> bool:
        '''Gets whether import materials for each object'''
        raise NotImplementedError()
    
    @enable_materials.setter
    def enable_materials(self, value : bool) -> None:
        '''Sets whether import materials for each object'''
        raise NotImplementedError()
    
    @property
    def scale(self) -> float:
        '''Scales on x/y/z axis, default value is 1.0'''
        raise NotImplementedError()
    
    @scale.setter
    def scale(self, value : float) -> None:
        '''Scales on x/y/z axis, default value is 1.0'''
        raise NotImplementedError()
    
    @property
    def normalize_normal(self) -> bool:
        '''Gets whether to normalize the normal vector during the loading.
        Default value is true.'''
        raise NotImplementedError()
    
    @normalize_normal.setter
    def normalize_normal(self, value : bool) -> None:
        '''Sets whether to normalize the normal vector during the loading.
        Default value is true.'''
        raise NotImplementedError()
    

class ObjSaveOptions(SaveOptions):
    '''Save options for wavefront obj file'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.ObjSaveOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def apply_unit_scale(self) -> bool:
        '''Apply :py:attr:`aspose.threed.AssetInfo.unit_scale_factor` to the mesh.
        Default value is false.'''
        raise NotImplementedError()
    
    @apply_unit_scale.setter
    def apply_unit_scale(self, value : bool) -> None:
        '''Apply :py:attr:`aspose.threed.AssetInfo.unit_scale_factor` to the mesh.
        Default value is false.'''
        raise NotImplementedError()
    
    @property
    def point_cloud(self) -> bool:
        '''Gets the flag whether the exporter should export the scene as point cloud(without topological structure), default value is false'''
        raise NotImplementedError()
    
    @point_cloud.setter
    def point_cloud(self, value : bool) -> None:
        '''Sets the flag whether the exporter should export the scene as point cloud(without topological structure), default value is false'''
        raise NotImplementedError()
    
    @property
    def verbose(self) -> bool:
        '''Gets whether generate comments for each section'''
        raise NotImplementedError()
    
    @verbose.setter
    def verbose(self, value : bool) -> None:
        '''Sets whether generate comments for each section'''
        raise NotImplementedError()
    
    @property
    def serialize_w(self) -> bool:
        '''Gets whether serialize W component in model\'s vertex position.'''
        raise NotImplementedError()
    
    @serialize_w.setter
    def serialize_w(self, value : bool) -> None:
        '''Sets whether serialize W component in model\'s vertex position.'''
        raise NotImplementedError()
    
    @property
    def enable_materials(self) -> bool:
        '''Gets whether import/export materials for each object'''
        raise NotImplementedError()
    
    @enable_materials.setter
    def enable_materials(self, value : bool) -> None:
        '''Sets whether import/export materials for each object'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate_system(self) -> bool:
        '''Gets whether flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    
    @flip_coordinate_system.setter
    def flip_coordinate_system(self, value : bool) -> None:
        '''Sets whether flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    
    @property
    def axis_system(self) -> aspose.threed.AxisSystem:
        '''Gets the axis system in the exported file.'''
        raise NotImplementedError()
    
    @axis_system.setter
    def axis_system(self, value : aspose.threed.AxisSystem) -> None:
        '''Sets the axis system in the exported file.'''
        raise NotImplementedError()
    

class PdfFormat(aspose.threed.FileFormat):
    '''Adobe\'s Portable Document Format'''
    
    @overload
    @staticmethod
    def detect(stream : io._IOBase, file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from data stream, file name is optional for guessing types that has no magic header.
        
        :param stream: Stream containing data to detect
        :param file_name: Original file name of the data, used as hint.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def detect(file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from file name, file must be readable so Aspose.3D can detect the file format through file header.
        
        :param file_name: Path to the file to detect file format.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @overload
    def extract(self, file_name : str, password : List[int]) -> List[List[int]]:
        '''Extract raw 3D content from PDF file.
        
        :param file_name: File name of input PDF file
        :param password: Password of the PDF file
        :returns: A list of all 3D contents in bytes, including the formats that Aspose.3D don\'t supported.'''
        raise NotImplementedError()
    
    @overload
    def extract(self, stream : io._IOBase, password : List[int]) -> List[List[int]]:
        '''Extract raw 3D content from PDF stream.
        
        :param stream: Stream of input PDF file
        :param password: Password of the PDF file
        :returns: A list of all 3D contents in bytes, including the formats that Aspose.3D don\'t supported.'''
        raise NotImplementedError()
    
    @overload
    def extract_scene(self, file_name : str) -> List[aspose.threed.Scene]:
        '''Extract 3D scenes from PDF file.
        
        :param file_name: File name of input PDF file
        :returns: List of decoded 3D scenes  that supported by Aspose.3D'''
        raise NotImplementedError()
    
    @overload
    def extract_scene(self, file_name : str, password : List[int]) -> List[aspose.threed.Scene]:
        '''Extract 3D scenes from PDF file.
        
        :param file_name: File name of input PDF file
        :param password: Password of the PDF file
        :returns: List of decoded 3D scenes  that supported by Aspose.3D'''
        raise NotImplementedError()
    
    @overload
    def extract_scene(self, stream : io._IOBase, password : List[int]) -> List[aspose.threed.Scene]:
        '''Extract raw 3D content from PDF stream.
        
        :param stream: Stream of input PDF file
        :param password: Password of the PDF file
        :returns: List of decoded 3D scenes  that supported by Aspose.3D'''
        raise NotImplementedError()
    
    @staticmethod
    def get_format_by_extension(extension_name : str) -> aspose.threed.FileFormat:
        '''Gets the preferred file format from the file extension name
        The extension name should starts with a dot(\'.\').
        
        :param extension_name: The extension name started with \'.\' to query.
        :returns: Instance of :py:class:`aspose.threed.FileFormat`, otherwise null returned.'''
        raise NotImplementedError()
    
    def create_load_options(self) -> aspose.threed.formats.LoadOptions:
        '''Create a default load options for this file format
        
        :returns: A default load option for current format'''
        raise NotImplementedError()
    
    def create_save_options(self) -> aspose.threed.formats.SaveOptions:
        '''Create a default save options for this file format
        
        :returns: A default save option for current format'''
        raise NotImplementedError()
    
    @property
    def formats(self) -> List[aspose.threed.FileFormat]:
        '''Access to all supported formats'''
        raise NotImplementedError()

    @property
    def version(self) -> tuple[int, int]:
        '''Gets file format version'''
        raise NotImplementedError()
    
    @property
    def can_export(self) -> bool:
        '''Gets whether Aspose.3D supports export scene to current file format.'''
        raise NotImplementedError()
    
    @property
    def can_import(self) -> bool:
        '''Gets whether Aspose.3D supports import scene from current file format.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''Gets the extension name of this type.'''
        raise NotImplementedError()
    
    @property
    def extensions(self) -> List[str]:
        '''Gets the extension names of this type.'''
        raise NotImplementedError()
    
    @property
    def content_type(self) -> aspose.threed.FileContentType:
        '''Gets file format content type'''
        raise NotImplementedError()
    
    @property
    def file_format_type(self) -> aspose.threed.FileFormatType:
        '''Gets file format type'''
        raise NotImplementedError()
    
    @property
    def FBX6100ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX6100_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def MAYA_ASCII(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in ASCII format'''
        raise NotImplementedError()

    @property
    def MAYA_BINARY(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in Binary format'''
        raise NotImplementedError()

    @property
    def STL_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary STL file format'''
        raise NotImplementedError()

    @property
    def STLASCII(self) -> aspose.threed.FileFormat:
        '''ASCII STL file format'''
        raise NotImplementedError()

    @property
    def WAVEFRONT_OBJ(self) -> aspose.threed.FileFormat:
        '''Wavefront\'s Obj file format'''
        raise NotImplementedError()

    @property
    def DISCREET_3DS(self) -> aspose.threed.FileFormat:
        '''3D Studio\'s file format'''
        raise NotImplementedError()

    @property
    def COLLADA(self) -> aspose.threed.FileFormat:
        '''Collada file format'''
        raise NotImplementedError()

    @property
    def UNIVERSAL_3D(self) -> aspose.threed.FileFormat:
        '''Universal3D file format'''
        raise NotImplementedError()

    @property
    def GLTF(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF'''
        raise NotImplementedError()

    @property
    def GLTF2(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def GLTF_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF in Binary format'''
        raise NotImplementedError()

    @property
    def GLTF2_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def PDF(self) -> aspose.threed.formats.PdfFormat:
        '''Adobe\'s Portable Document Format'''
        raise NotImplementedError()

    @property
    def BLENDER(self) -> aspose.threed.FileFormat:
        '''Blender\'s 3D file format'''
        raise NotImplementedError()

    @property
    def DXF(self) -> aspose.threed.FileFormat:
        '''AutoCAD DXF'''
        raise NotImplementedError()

    @property
    def PLY(self) -> aspose.threed.formats.PlyFormat:
        '''Polygon File Format or Stanford Triangle Format'''
        raise NotImplementedError()

    @property
    def X_BINARY(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def X_TEXT(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def DRACO(self) -> aspose.threed.formats.DracoFormat:
        '''Google Draco Mesh'''
        raise NotImplementedError()

    @property
    def MICROSOFT_3MF(self) -> aspose.threed.formats.Microsoft3MFFormat:
        '''Microsoft 3D Manufacturing Format'''
        raise NotImplementedError()

    @property
    def RVM_TEXT(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in text format'''
        raise NotImplementedError()

    @property
    def RVM_BINARY(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in binary format'''
        raise NotImplementedError()

    @property
    def ASE(self) -> aspose.threed.FileFormat:
        '''3D Studio Max\'s ASCII Scene Exporter format.'''
        raise NotImplementedError()

    @property
    def IFC(self) -> aspose.threed.FileFormat:
        '''ISO 16739-1 Industry Foundation Classes data model.'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT8(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 8'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT9(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 9'''
        raise NotImplementedError()

    @property
    def AMF(self) -> aspose.threed.FileFormat:
        '''Additive manufacturing file format'''
        raise NotImplementedError()

    @property
    def VRML(self) -> aspose.threed.FileFormat:
        '''The Virtual Reality Modeling Language'''
        raise NotImplementedError()

    @property
    def ASPOSE_3D_WEB(self) -> aspose.threed.FileFormat:
        '''Aspose.3D Web format.'''
        raise NotImplementedError()

    @property
    def HTML5(self) -> aspose.threed.FileFormat:
        '''HTML5 File'''
        raise NotImplementedError()

    @property
    def ZIP(self) -> aspose.threed.FileFormat:
        '''Zip archive that contains other 3d file format.'''
        raise NotImplementedError()

    @property
    def USD(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description'''
        raise NotImplementedError()

    @property
    def USDA(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description in ASCII format.'''
        raise NotImplementedError()

    @property
    def USDZ(self) -> aspose.threed.FileFormat:
        '''Compressed Universal Scene Description'''
        raise NotImplementedError()

    @property
    def XYZ(self) -> aspose.threed.FileFormat:
        '''Xyz point cloud file'''
        raise NotImplementedError()

    @property
    def PCD(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in ASCII mode'''
        raise NotImplementedError()

    @property
    def PCD_BINARY(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in Binary mode'''
        raise NotImplementedError()


class PdfLoadOptions(LoadOptions):
    '''Options for PDF loading'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.PdfLoadOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def password(self) -> List[int]:
        '''The password to unlock the encrypted PDF file.'''
        raise NotImplementedError()
    
    @password.setter
    def password(self, value : List[int]) -> None:
        '''The password to unlock the encrypted PDF file.'''
        raise NotImplementedError()
    

class PdfSaveOptions(SaveOptions):
    '''The save options in PDF exporting.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.PdfSaveOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def render_mode(self) -> aspose.threed.formats.PdfRenderMode:
        '''Render mode specifies the style in which the 3D artwork is rendered.'''
        raise NotImplementedError()
    
    @render_mode.setter
    def render_mode(self, value : aspose.threed.formats.PdfRenderMode) -> None:
        '''Render mode specifies the style in which the 3D artwork is rendered.'''
        raise NotImplementedError()
    
    @property
    def lighting_scheme(self) -> aspose.threed.formats.PdfLightingScheme:
        '''LightingScheme specifies the lighting to apply to 3D artwork.'''
        raise NotImplementedError()
    
    @lighting_scheme.setter
    def lighting_scheme(self, value : aspose.threed.formats.PdfLightingScheme) -> None:
        '''LightingScheme specifies the lighting to apply to 3D artwork.'''
        raise NotImplementedError()
    
    @property
    def background_color(self) -> aspose.threed.utilities.Vector3:
        '''Background color of the 3D view in PDF file.'''
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Background color of the 3D view in PDF file.'''
        raise NotImplementedError()
    
    @property
    def face_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the face color to be used  when rendering the 3D content.
        This is only relevant only when the :py:attr:`aspose.threed.formats.PdfSaveOptions.render_mode` has a value of Illustration.'''
        raise NotImplementedError()
    
    @face_color.setter
    def face_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the face color to be used  when rendering the 3D content.
        This is only relevant only when the :py:attr:`aspose.threed.formats.PdfSaveOptions.render_mode` has a value of Illustration.'''
        raise NotImplementedError()
    
    @property
    def auxiliary_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the auxiliary color to be used  when rendering the 3D content.
        The interpretation of this color depends on the :py:attr:`aspose.threed.formats.PdfSaveOptions.render_mode`'''
        raise NotImplementedError()
    
    @auxiliary_color.setter
    def auxiliary_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the auxiliary color to be used  when rendering the 3D content.
        The interpretation of this color depends on the :py:attr:`aspose.threed.formats.PdfSaveOptions.render_mode`'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate_system(self) -> bool:
        '''Gets to flip the coordinate system of the scene during exporting.'''
        raise NotImplementedError()
    
    @flip_coordinate_system.setter
    def flip_coordinate_system(self, value : bool) -> None:
        '''Sets to flip the coordinate system of the scene during exporting.'''
        raise NotImplementedError()
    
    @property
    def embed_textures(self) -> bool:
        '''Embed the external textures into the PDF file, default value is false.'''
        raise NotImplementedError()
    
    @embed_textures.setter
    def embed_textures(self, value : bool) -> None:
        '''Embed the external textures into the PDF file, default value is false.'''
        raise NotImplementedError()
    

class PlyFormat(aspose.threed.FileFormat):
    '''The PLY format.'''
    
    @overload
    @staticmethod
    def detect(stream : io._IOBase, file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from data stream, file name is optional for guessing types that has no magic header.
        
        :param stream: Stream containing data to detect
        :param file_name: Original file name of the data, used as hint.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def detect(file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from file name, file must be readable so Aspose.3D can detect the file format through file header.
        
        :param file_name: Path to the file to detect file format.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @overload
    def encode(self, entity : aspose.threed.Entity, stream : io._IOBase) -> None:
        '''Encode the entity and save the result into the stream.
        
        :param entity: The entity to encode
        :param stream: The stream to write to, this method will not close this stream'''
        raise NotImplementedError()
    
    @overload
    def encode(self, entity : aspose.threed.Entity, stream : io._IOBase, opt : aspose.threed.formats.PlySaveOptions) -> None:
        '''Encode the entity and save the result into the stream.
        
        :param entity: The entity to encode
        :param stream: The stream to write to, this method will not close this stream
        :param opt: Save options'''
        raise NotImplementedError()
    
    @overload
    def encode(self, entity : aspose.threed.Entity, file_name : str) -> None:
        '''Encode the entity and save the result into an external file.
        
        :param entity: The entity to encode
        :param file_name: The file to write to'''
        raise NotImplementedError()
    
    @overload
    def encode(self, entity : aspose.threed.Entity, file_name : str, opt : aspose.threed.formats.PlySaveOptions) -> None:
        '''Encode the entity and save the result into an external file.
        
        :param entity: The entity to encode
        :param file_name: The file to write to
        :param opt: Save options'''
        raise NotImplementedError()
    
    @overload
    def decode(self, file_name : str) -> aspose.threed.entities.Geometry:
        '''Decode a point cloud or mesh from the specified stream.
        
        :param file_name: The input stream
        :returns: A :py:class:`aspose.threed.entities.Mesh` or :py:class:`aspose.threed.entities.PointCloud` instance'''
        raise NotImplementedError()
    
    @overload
    def decode(self, file_name : str, opt : aspose.threed.formats.PlyLoadOptions) -> aspose.threed.entities.Geometry:
        '''Decode a point cloud or mesh from the specified stream.
        
        :param file_name: The input stream
        :param opt: The load option of PLY format
        :returns: A :py:class:`aspose.threed.entities.Mesh` or :py:class:`aspose.threed.entities.PointCloud` instance'''
        raise NotImplementedError()
    
    @overload
    def decode(self, stream : io._IOBase) -> aspose.threed.entities.Geometry:
        '''Decode a point cloud or mesh from the specified stream.
        
        :param stream: The input stream
        :returns: A :py:class:`aspose.threed.entities.Mesh` or :py:class:`aspose.threed.entities.PointCloud` instance'''
        raise NotImplementedError()
    
    @overload
    def decode(self, stream : io._IOBase, opt : aspose.threed.formats.PlyLoadOptions) -> aspose.threed.entities.Geometry:
        '''Decode a point cloud or mesh from the specified stream.
        
        :param stream: The input stream
        :param opt: The load option of PLY format
        :returns: A :py:class:`aspose.threed.entities.Mesh` or :py:class:`aspose.threed.entities.PointCloud` instance'''
        raise NotImplementedError()
    
    @staticmethod
    def get_format_by_extension(extension_name : str) -> aspose.threed.FileFormat:
        '''Gets the preferred file format from the file extension name
        The extension name should starts with a dot(\'.\').
        
        :param extension_name: The extension name started with \'.\' to query.
        :returns: Instance of :py:class:`aspose.threed.FileFormat`, otherwise null returned.'''
        raise NotImplementedError()
    
    def create_load_options(self) -> aspose.threed.formats.LoadOptions:
        '''Create a default load options for this file format
        
        :returns: A default load option for current format'''
        raise NotImplementedError()
    
    def create_save_options(self) -> aspose.threed.formats.SaveOptions:
        '''Create a default save options for this file format
        
        :returns: A default save option for current format'''
        raise NotImplementedError()
    
    @property
    def formats(self) -> List[aspose.threed.FileFormat]:
        '''Access to all supported formats'''
        raise NotImplementedError()

    @property
    def version(self) -> tuple[int, int]:
        '''Gets file format version'''
        raise NotImplementedError()
    
    @property
    def can_export(self) -> bool:
        '''Gets whether Aspose.3D supports export scene to current file format.'''
        raise NotImplementedError()
    
    @property
    def can_import(self) -> bool:
        '''Gets whether Aspose.3D supports import scene from current file format.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''Gets the extension name of this type.'''
        raise NotImplementedError()
    
    @property
    def extensions(self) -> List[str]:
        '''Gets the extension names of this type.'''
        raise NotImplementedError()
    
    @property
    def content_type(self) -> aspose.threed.FileContentType:
        '''Gets file format content type'''
        raise NotImplementedError()
    
    @property
    def file_format_type(self) -> aspose.threed.FileFormatType:
        '''Gets file format type'''
        raise NotImplementedError()
    
    @property
    def FBX6100ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX6100_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def MAYA_ASCII(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in ASCII format'''
        raise NotImplementedError()

    @property
    def MAYA_BINARY(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in Binary format'''
        raise NotImplementedError()

    @property
    def STL_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary STL file format'''
        raise NotImplementedError()

    @property
    def STLASCII(self) -> aspose.threed.FileFormat:
        '''ASCII STL file format'''
        raise NotImplementedError()

    @property
    def WAVEFRONT_OBJ(self) -> aspose.threed.FileFormat:
        '''Wavefront\'s Obj file format'''
        raise NotImplementedError()

    @property
    def DISCREET_3DS(self) -> aspose.threed.FileFormat:
        '''3D Studio\'s file format'''
        raise NotImplementedError()

    @property
    def COLLADA(self) -> aspose.threed.FileFormat:
        '''Collada file format'''
        raise NotImplementedError()

    @property
    def UNIVERSAL_3D(self) -> aspose.threed.FileFormat:
        '''Universal3D file format'''
        raise NotImplementedError()

    @property
    def GLTF(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF'''
        raise NotImplementedError()

    @property
    def GLTF2(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def GLTF_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF in Binary format'''
        raise NotImplementedError()

    @property
    def GLTF2_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def PDF(self) -> aspose.threed.formats.PdfFormat:
        '''Adobe\'s Portable Document Format'''
        raise NotImplementedError()

    @property
    def BLENDER(self) -> aspose.threed.FileFormat:
        '''Blender\'s 3D file format'''
        raise NotImplementedError()

    @property
    def DXF(self) -> aspose.threed.FileFormat:
        '''AutoCAD DXF'''
        raise NotImplementedError()

    @property
    def PLY(self) -> aspose.threed.formats.PlyFormat:
        '''Polygon File Format or Stanford Triangle Format'''
        raise NotImplementedError()

    @property
    def X_BINARY(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def X_TEXT(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def DRACO(self) -> aspose.threed.formats.DracoFormat:
        '''Google Draco Mesh'''
        raise NotImplementedError()

    @property
    def MICROSOFT_3MF(self) -> aspose.threed.formats.Microsoft3MFFormat:
        '''Microsoft 3D Manufacturing Format'''
        raise NotImplementedError()

    @property
    def RVM_TEXT(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in text format'''
        raise NotImplementedError()

    @property
    def RVM_BINARY(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in binary format'''
        raise NotImplementedError()

    @property
    def ASE(self) -> aspose.threed.FileFormat:
        '''3D Studio Max\'s ASCII Scene Exporter format.'''
        raise NotImplementedError()

    @property
    def IFC(self) -> aspose.threed.FileFormat:
        '''ISO 16739-1 Industry Foundation Classes data model.'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT8(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 8'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT9(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 9'''
        raise NotImplementedError()

    @property
    def AMF(self) -> aspose.threed.FileFormat:
        '''Additive manufacturing file format'''
        raise NotImplementedError()

    @property
    def VRML(self) -> aspose.threed.FileFormat:
        '''The Virtual Reality Modeling Language'''
        raise NotImplementedError()

    @property
    def ASPOSE_3D_WEB(self) -> aspose.threed.FileFormat:
        '''Aspose.3D Web format.'''
        raise NotImplementedError()

    @property
    def HTML5(self) -> aspose.threed.FileFormat:
        '''HTML5 File'''
        raise NotImplementedError()

    @property
    def ZIP(self) -> aspose.threed.FileFormat:
        '''Zip archive that contains other 3d file format.'''
        raise NotImplementedError()

    @property
    def USD(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description'''
        raise NotImplementedError()

    @property
    def USDA(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description in ASCII format.'''
        raise NotImplementedError()

    @property
    def USDZ(self) -> aspose.threed.FileFormat:
        '''Compressed Universal Scene Description'''
        raise NotImplementedError()

    @property
    def XYZ(self) -> aspose.threed.FileFormat:
        '''Xyz point cloud file'''
        raise NotImplementedError()

    @property
    def PCD(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in ASCII mode'''
        raise NotImplementedError()

    @property
    def PCD_BINARY(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in Binary mode'''
        raise NotImplementedError()


class PlyLoadOptions(LoadOptions):
    '''Load options for PLY files'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.PlyLoadOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate_system(self) -> bool:
        '''Gets flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    
    @flip_coordinate_system.setter
    def flip_coordinate_system(self, value : bool) -> None:
        '''Sets flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    

class PlySaveOptions(SaveOptions):
    '''Save options for exporting scene as PLY file.'''
    
    @overload
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.PlySaveOptions`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, content_type : aspose.threed.FileContentType) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.PlySaveOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def point_cloud(self) -> bool:
        '''Export the scene as point cloud, the default value is false.'''
        raise NotImplementedError()
    
    @point_cloud.setter
    def point_cloud(self, value : bool) -> None:
        '''Export the scene as point cloud, the default value is false.'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate(self) -> bool:
        '''Flip the coordinate while saving the scene, default value is true'''
        raise NotImplementedError()
    
    @flip_coordinate.setter
    def flip_coordinate(self, value : bool) -> None:
        '''Flip the coordinate while saving the scene, default value is true'''
        raise NotImplementedError()
    
    @property
    def vertex_element(self) -> str:
        '''The element name for the vertex data, default value is "vertex"'''
        raise NotImplementedError()
    
    @vertex_element.setter
    def vertex_element(self, value : str) -> None:
        '''The element name for the vertex data, default value is "vertex"'''
        raise NotImplementedError()
    
    @property
    def face_element(self) -> str:
        '''The element name for the face data, default value is "face"'''
        raise NotImplementedError()
    
    @face_element.setter
    def face_element(self, value : str) -> None:
        '''The element name for the face data, default value is "face"'''
        raise NotImplementedError()
    
    @property
    def face_property(self) -> str:
        '''The property name for the face data, default value is "vertex_index"'''
        raise NotImplementedError()
    
    @face_property.setter
    def face_property(self, value : str) -> None:
        '''The property name for the face data, default value is "vertex_index"'''
        raise NotImplementedError()
    
    @property
    def axis_system(self) -> aspose.threed.AxisSystem:
        '''Gets the axis system in the exported stl file.'''
        raise NotImplementedError()
    
    @axis_system.setter
    def axis_system(self, value : aspose.threed.AxisSystem) -> None:
        '''Sets the axis system in the exported stl file.'''
        raise NotImplementedError()
    

class RvmFormat(aspose.threed.FileFormat):
    '''The RVM Format'''
    
    @overload
    @staticmethod
    def detect(stream : io._IOBase, file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from data stream, file name is optional for guessing types that has no magic header.
        
        :param stream: Stream containing data to detect
        :param file_name: Original file name of the data, used as hint.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def detect(file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from file name, file must be readable so Aspose.3D can detect the file format through file header.
        
        :param file_name: Path to the file to detect file format.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @overload
    def load_attributes(self, scene : aspose.threed.Scene, file_name : str, prefix : str) -> None:
        '''Load the attributes from specified file name
        
        :param scene: The scene where the attributes will be applied to
        :param file_name: The file\'s name that contains the attributes
        :param prefix: The prefix of the attributes that used to avoid conflict of names, default value is "rvm:"'''
        raise NotImplementedError()
    
    @overload
    def load_attributes(self, scene : aspose.threed.Scene, stream : io._IOBase, prefix : str) -> None:
        '''Load the attributes from specified stream
        
        :param scene: The scene where the attributes will be applied to
        :param stream: The stream that contains the attributes
        :param prefix: The prefix of the attributes that used to avoid conflict of names, default value is "rvm:"'''
        raise NotImplementedError()
    
    @staticmethod
    def get_format_by_extension(extension_name : str) -> aspose.threed.FileFormat:
        '''Gets the preferred file format from the file extension name
        The extension name should starts with a dot(\'.\').
        
        :param extension_name: The extension name started with \'.\' to query.
        :returns: Instance of :py:class:`aspose.threed.FileFormat`, otherwise null returned.'''
        raise NotImplementedError()
    
    def create_load_options(self) -> aspose.threed.formats.LoadOptions:
        '''Create a default load options for this file format
        
        :returns: A default load option for current format'''
        raise NotImplementedError()
    
    def create_save_options(self) -> aspose.threed.formats.SaveOptions:
        '''Create a default save options for this file format
        
        :returns: A default save option for current format'''
        raise NotImplementedError()
    
    @property
    def formats(self) -> List[aspose.threed.FileFormat]:
        '''Access to all supported formats'''
        raise NotImplementedError()

    @property
    def version(self) -> tuple[int, int]:
        '''Gets file format version'''
        raise NotImplementedError()
    
    @property
    def can_export(self) -> bool:
        '''Gets whether Aspose.3D supports export scene to current file format.'''
        raise NotImplementedError()
    
    @property
    def can_import(self) -> bool:
        '''Gets whether Aspose.3D supports import scene from current file format.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''Gets the extension name of this type.'''
        raise NotImplementedError()
    
    @property
    def extensions(self) -> List[str]:
        '''Gets the extension names of this type.'''
        raise NotImplementedError()
    
    @property
    def content_type(self) -> aspose.threed.FileContentType:
        '''Gets file format content type'''
        raise NotImplementedError()
    
    @property
    def file_format_type(self) -> aspose.threed.FileFormatType:
        '''Gets file format type'''
        raise NotImplementedError()
    
    @property
    def FBX6100ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX6100_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def MAYA_ASCII(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in ASCII format'''
        raise NotImplementedError()

    @property
    def MAYA_BINARY(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in Binary format'''
        raise NotImplementedError()

    @property
    def STL_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary STL file format'''
        raise NotImplementedError()

    @property
    def STLASCII(self) -> aspose.threed.FileFormat:
        '''ASCII STL file format'''
        raise NotImplementedError()

    @property
    def WAVEFRONT_OBJ(self) -> aspose.threed.FileFormat:
        '''Wavefront\'s Obj file format'''
        raise NotImplementedError()

    @property
    def DISCREET_3DS(self) -> aspose.threed.FileFormat:
        '''3D Studio\'s file format'''
        raise NotImplementedError()

    @property
    def COLLADA(self) -> aspose.threed.FileFormat:
        '''Collada file format'''
        raise NotImplementedError()

    @property
    def UNIVERSAL_3D(self) -> aspose.threed.FileFormat:
        '''Universal3D file format'''
        raise NotImplementedError()

    @property
    def GLTF(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF'''
        raise NotImplementedError()

    @property
    def GLTF2(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def GLTF_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF in Binary format'''
        raise NotImplementedError()

    @property
    def GLTF2_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def PDF(self) -> aspose.threed.formats.PdfFormat:
        '''Adobe\'s Portable Document Format'''
        raise NotImplementedError()

    @property
    def BLENDER(self) -> aspose.threed.FileFormat:
        '''Blender\'s 3D file format'''
        raise NotImplementedError()

    @property
    def DXF(self) -> aspose.threed.FileFormat:
        '''AutoCAD DXF'''
        raise NotImplementedError()

    @property
    def PLY(self) -> aspose.threed.formats.PlyFormat:
        '''Polygon File Format or Stanford Triangle Format'''
        raise NotImplementedError()

    @property
    def X_BINARY(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def X_TEXT(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def DRACO(self) -> aspose.threed.formats.DracoFormat:
        '''Google Draco Mesh'''
        raise NotImplementedError()

    @property
    def MICROSOFT_3MF(self) -> aspose.threed.formats.Microsoft3MFFormat:
        '''Microsoft 3D Manufacturing Format'''
        raise NotImplementedError()

    @property
    def RVM_TEXT(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in text format'''
        raise NotImplementedError()

    @property
    def RVM_BINARY(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in binary format'''
        raise NotImplementedError()

    @property
    def ASE(self) -> aspose.threed.FileFormat:
        '''3D Studio Max\'s ASCII Scene Exporter format.'''
        raise NotImplementedError()

    @property
    def IFC(self) -> aspose.threed.FileFormat:
        '''ISO 16739-1 Industry Foundation Classes data model.'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT8(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 8'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT9(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 9'''
        raise NotImplementedError()

    @property
    def AMF(self) -> aspose.threed.FileFormat:
        '''Additive manufacturing file format'''
        raise NotImplementedError()

    @property
    def VRML(self) -> aspose.threed.FileFormat:
        '''The Virtual Reality Modeling Language'''
        raise NotImplementedError()

    @property
    def ASPOSE_3D_WEB(self) -> aspose.threed.FileFormat:
        '''Aspose.3D Web format.'''
        raise NotImplementedError()

    @property
    def HTML5(self) -> aspose.threed.FileFormat:
        '''HTML5 File'''
        raise NotImplementedError()

    @property
    def ZIP(self) -> aspose.threed.FileFormat:
        '''Zip archive that contains other 3d file format.'''
        raise NotImplementedError()

    @property
    def USD(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description'''
        raise NotImplementedError()

    @property
    def USDA(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description in ASCII format.'''
        raise NotImplementedError()

    @property
    def USDZ(self) -> aspose.threed.FileFormat:
        '''Compressed Universal Scene Description'''
        raise NotImplementedError()

    @property
    def XYZ(self) -> aspose.threed.FileFormat:
        '''Xyz point cloud file'''
        raise NotImplementedError()

    @property
    def PCD(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in ASCII mode'''
        raise NotImplementedError()

    @property
    def PCD_BINARY(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in Binary mode'''
        raise NotImplementedError()


class RvmLoadOptions(LoadOptions):
    '''Load options for AVEVA Plant Design Management System\'s RVM file.'''
    
    @overload
    def __init__(self, content_type : aspose.threed.FileContentType) -> None:
        '''Construct a :py:class:`aspose.threed.formats.RvmLoadOptions` instance'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Construct a :py:class:`aspose.threed.formats.RvmLoadOptions` instance'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def generate_materials(self) -> bool:
        '''Generate materials with random colors for each objects in the scene if color table is not exported within the RVM file.
        Default value is true'''
        raise NotImplementedError()
    
    @generate_materials.setter
    def generate_materials(self, value : bool) -> None:
        '''Generate materials with random colors for each objects in the scene if color table is not exported within the RVM file.
        Default value is true'''
        raise NotImplementedError()
    
    @property
    def cylinder_radial_segments(self) -> int:
        '''Gets the number of cylinder\'s radial segments, default value is 16'''
        raise NotImplementedError()
    
    @cylinder_radial_segments.setter
    def cylinder_radial_segments(self, value : int) -> None:
        '''Sets the number of cylinder\'s radial segments, default value is 16'''
        raise NotImplementedError()
    
    @property
    def dish_longitude_segments(self) -> int:
        '''Gets the number of dish\' longitude segments, default value is 12'''
        raise NotImplementedError()
    
    @dish_longitude_segments.setter
    def dish_longitude_segments(self, value : int) -> None:
        '''Sets the number of dish\' longitude segments, default value is 12'''
        raise NotImplementedError()
    
    @property
    def dish_latitude_segments(self) -> int:
        '''Gets the number of dish\' latitude segments, default value is 8'''
        raise NotImplementedError()
    
    @dish_latitude_segments.setter
    def dish_latitude_segments(self, value : int) -> None:
        '''Sets the number of dish\' latitude segments, default value is 8'''
        raise NotImplementedError()
    
    @property
    def torus_tubular_segments(self) -> int:
        '''Gets the number of torus\' tubular segments, default value is 20'''
        raise NotImplementedError()
    
    @torus_tubular_segments.setter
    def torus_tubular_segments(self, value : int) -> None:
        '''Sets the number of torus\' tubular segments, default value is 20'''
        raise NotImplementedError()
    
    @property
    def rectangular_torus_segments(self) -> int:
        '''Gets the number of rectangular torus\' radial segments, default value is 20'''
        raise NotImplementedError()
    
    @rectangular_torus_segments.setter
    def rectangular_torus_segments(self, value : int) -> None:
        '''Sets the number of rectangular torus\' radial segments, default value is 20'''
        raise NotImplementedError()
    
    @property
    def center_scene(self) -> bool:
        '''Center the scene after it\'s loaded.'''
        raise NotImplementedError()
    
    @center_scene.setter
    def center_scene(self, value : bool) -> None:
        '''Center the scene after it\'s loaded.'''
        raise NotImplementedError()
    
    @property
    def attribute_prefix(self) -> str:
        '''Gets the prefix of the attributes that were defined in external attribute files,
        The prefix are used to avoid name conflicts, default value is "rvm:"'''
        raise NotImplementedError()
    
    @attribute_prefix.setter
    def attribute_prefix(self, value : str) -> None:
        '''Sets the prefix of the attributes that were defined in external attribute files,
        The prefix are used to avoid name conflicts, default value is "rvm:"'''
        raise NotImplementedError()
    
    @property
    def lookup_attributes(self) -> bool:
        '''Gets whether to load attributes from external attribute list file(.att/.attrib/.txt), default value is true.'''
        raise NotImplementedError()
    
    @lookup_attributes.setter
    def lookup_attributes(self, value : bool) -> None:
        '''Sets whether to load attributes from external attribute list file(.att/.attrib/.txt), default value is true.'''
        raise NotImplementedError()
    

class RvmSaveOptions(SaveOptions):
    '''Save options for Aveva PDMS RVM file.'''
    
    @overload
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.RvmSaveOptions`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, content_type : aspose.threed.FileContentType) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.RvmSaveOptions`
        
        :param content_type: Text or binary RVM file?'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def file_note(self) -> str:
        '''File note in the file header.'''
        raise NotImplementedError()
    
    @file_note.setter
    def file_note(self, value : str) -> None:
        '''File note in the file header.'''
        raise NotImplementedError()
    
    @property
    def author(self) -> str:
        '''Author information, default value is \'3d@aspose\''''
        raise NotImplementedError()
    
    @author.setter
    def author(self, value : str) -> None:
        '''Author information, default value is \'3d@aspose\''''
        raise NotImplementedError()
    
    @property
    def creation_time(self) -> str:
        '''The timestamp that exported this file, default value is current time'''
        raise NotImplementedError()
    
    @creation_time.setter
    def creation_time(self, value : str) -> None:
        '''The timestamp that exported this file, default value is current time'''
        raise NotImplementedError()
    
    @property
    def attribute_prefix(self) -> str:
        '''Gets the prefix of which attributes that will be exported, the exported property will contains no prefix, custom properties with different prefix will not be exported, default value is \'rvm:\'.
        For example if a property is rvm:Refno=345, the exported attribute will be Refno = 345, the prefix is stripped.'''
        raise NotImplementedError()
    
    @attribute_prefix.setter
    def attribute_prefix(self, value : str) -> None:
        '''Sets the prefix of which attributes that will be exported, the exported property will contains no prefix, custom properties with different prefix will not be exported, default value is \'rvm:\'.
        For example if a property is rvm:Refno=345, the exported attribute will be Refno = 345, the prefix is stripped.'''
        raise NotImplementedError()
    
    @property
    def attribute_list_file(self) -> str:
        '''Gets the file name of attribute list file, exporter will generate a name based on the .rvm file name when this property is undefined, default value is null.'''
        raise NotImplementedError()
    
    @attribute_list_file.setter
    def attribute_list_file(self, value : str) -> None:
        '''Sets the file name of attribute list file, exporter will generate a name based on the .rvm file name when this property is undefined, default value is null.'''
        raise NotImplementedError()
    
    @property
    def export_attributes(self) -> bool:
        '''Gets whether to export the attribute list to an external .att file, default value is false.'''
        raise NotImplementedError()
    
    @export_attributes.setter
    def export_attributes(self, value : bool) -> None:
        '''Sets whether to export the attribute list to an external .att file, default value is false.'''
        raise NotImplementedError()
    

class SaveOptions(IOConfig):
    '''The base class to configure options in file saving for different types'''
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    

class StlLoadOptions(LoadOptions):
    '''Load options for STL'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes of a new :py:class:`aspose.threed.formats.StlLoadOptions` instance.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, content_type : aspose.threed.FileContentType) -> None:
        '''Initializes of a new :py:class:`aspose.threed.formats.StlLoadOptions` instance.'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate_system(self) -> bool:
        '''Gets whether to flip coordinate system of control points/normal during importing.'''
        raise NotImplementedError()
    
    @flip_coordinate_system.setter
    def flip_coordinate_system(self, value : bool) -> None:
        '''Sets whether to flip coordinate system of control points/normal during importing.'''
        raise NotImplementedError()
    
    @property
    def recalculate_normal(self) -> bool:
        '''Ignore the normal data that stored in STL file and recalculate the normal data based on the vertex position.
        Default value is false'''
        raise NotImplementedError()
    
    @recalculate_normal.setter
    def recalculate_normal(self, value : bool) -> None:
        '''Ignore the normal data that stored in STL file and recalculate the normal data based on the vertex position.
        Default value is false'''
        raise NotImplementedError()
    

class StlSaveOptions(SaveOptions):
    '''Save options for STL'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes of a new :py:class:`aspose.threed.formats.StlSaveOptions` instance.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, content_type : aspose.threed.FileContentType) -> None:
        '''Initializes of a new :py:class:`aspose.threed.formats.StlSaveOptions` instance.'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def axis_system(self) -> aspose.threed.AxisSystem:
        '''Gets the axis system in the exported stl file.'''
        raise NotImplementedError()
    
    @axis_system.setter
    def axis_system(self, value : aspose.threed.AxisSystem) -> None:
        '''Sets the axis system in the exported stl file.'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate_system(self) -> bool:
        '''Gets whether flip coordinate system of control points/normal during exporting.'''
        raise NotImplementedError()
    
    @flip_coordinate_system.setter
    def flip_coordinate_system(self, value : bool) -> None:
        '''Sets whether flip coordinate system of control points/normal during exporting.'''
        raise NotImplementedError()
    

class U3dLoadOptions(LoadOptions):
    '''Load options for universal 3d'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.U3dLoadOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate_system(self) -> bool:
        '''Gets whether flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    
    @flip_coordinate_system.setter
    def flip_coordinate_system(self, value : bool) -> None:
        '''Sets whether flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    

class U3dSaveOptions(SaveOptions):
    '''Save options for universal 3d'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.U3dSaveOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate_system(self) -> bool:
        '''Gets whether flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    
    @flip_coordinate_system.setter
    def flip_coordinate_system(self, value : bool) -> None:
        '''Sets whether flip coordinate system of control points/normal during importing/exporting.'''
        raise NotImplementedError()
    
    @property
    def mesh_compression(self) -> bool:
        '''Gets whether to enable mesh data compression.'''
        raise NotImplementedError()
    
    @mesh_compression.setter
    def mesh_compression(self, value : bool) -> None:
        '''Sets whether to enable mesh data compression.'''
        raise NotImplementedError()
    
    @property
    def export_normals(self) -> bool:
        '''Gets whether to export normal data.'''
        raise NotImplementedError()
    
    @export_normals.setter
    def export_normals(self, value : bool) -> None:
        '''Sets whether to export normal data.'''
        raise NotImplementedError()
    
    @property
    def export_texture_coordinates(self) -> bool:
        '''Gets whether to export texture coordinates.'''
        raise NotImplementedError()
    
    @export_texture_coordinates.setter
    def export_texture_coordinates(self, value : bool) -> None:
        '''Sets whether to export texture coordinates.'''
        raise NotImplementedError()
    
    @property
    def export_vertex_diffuse(self) -> bool:
        '''Gets whether to export vertex\'s diffuse color.'''
        raise NotImplementedError()
    
    @export_vertex_diffuse.setter
    def export_vertex_diffuse(self, value : bool) -> None:
        '''Sets whether to export vertex\'s diffuse color.'''
        raise NotImplementedError()
    
    @property
    def export_vertex_specular(self) -> bool:
        '''Gets whether to export vertex\' specular color.'''
        raise NotImplementedError()
    
    @export_vertex_specular.setter
    def export_vertex_specular(self, value : bool) -> None:
        '''Sets whether to export vertex\' specular color.'''
        raise NotImplementedError()
    
    @property
    def embed_textures(self) -> bool:
        '''Embed the external textures into the U3D file, default value is false.'''
        raise NotImplementedError()
    
    @embed_textures.setter
    def embed_textures(self, value : bool) -> None:
        '''Embed the external textures into the U3D file, default value is false.'''
        raise NotImplementedError()
    

class UsdSaveOptions(SaveOptions):
    '''Save options for USD/USDZ formats.'''
    
    @overload
    def __init__(self) -> None:
        '''Initialize a new :py:class:`aspose.threed.formats.UsdSaveOptions` with :py:attr:`aspose.threed.FileFormat.USD` format'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_format : aspose.threed.FileFormat) -> None:
        '''Initialize a new :py:class:`aspose.threed.formats.UsdSaveOptions` with specified USD/USDZ format.'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def export_textures(self) -> bool:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @export_textures.setter
    def export_textures(self, value : bool) -> None:
        '''Try to copy textures used in scene to output directory.'''
        raise NotImplementedError()
    
    @property
    def primitive_to_mesh(self) -> bool:
        '''Convert the primitive entities to mesh during the export.
        Or directly encode the primitives to the output file(will use Aspose\'s extension definition for unofficial primitives like Dish, Torus)
        Default value is true.'''
        raise NotImplementedError()
    
    @primitive_to_mesh.setter
    def primitive_to_mesh(self, value : bool) -> None:
        '''Convert the primitive entities to mesh during the export.
        Or directly encode the primitives to the output file(will use Aspose\'s extension definition for unofficial primitives like Dish, Torus)
        Default value is true.'''
        raise NotImplementedError()
    
    @property
    def export_meta_data(self) -> bool:
        '''Export node\'s properties through USD\'s customData field.'''
        raise NotImplementedError()
    
    @export_meta_data.setter
    def export_meta_data(self, value : bool) -> None:
        '''Export node\'s properties through USD\'s customData field.'''
        raise NotImplementedError()
    

class XLoadOptions(LoadOptions):
    '''The Load options for DirectX X files.'''
    
    def __init__(self, content_type : aspose.threed.FileContentType) -> None:
        '''Constructor of :py:class:`aspose.threed.formats.XLoadOptions`'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> aspose.threed.FileFormat:
        '''Gets the file format that specified in current Save/Load option.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''Gets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        '''Sets the default encoding for text-based files.
        Default value is null which means the importer/exporter will decide which encoding to use.'''
        raise NotImplementedError()
    
    @property
    def file_system(self) -> aspose.threed.utilities.FileSystem:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @file_system.setter
    def file_system(self, value : aspose.threed.utilities.FileSystem) -> None:
        '''Allow user to handle how to manage the external dependencies during load/save.'''
        raise NotImplementedError()
    
    @property
    def lookup_paths(self) -> List[str]:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @lookup_paths.setter
    def lookup_paths(self, value : List[str]) -> None:
        '''Some files like OBJ depends on external file, the lookup paths will allows Aspose.3D to look for external file to load.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''The file name of the exporting/importing scene.
        This is optional, but useful when serialize external assets like OBJ\'s material.'''
        raise NotImplementedError()
    
    @property
    def flip_coordinate_system(self) -> bool:
        '''Flip the coordinate system, this is true by default'''
        raise NotImplementedError()
    
    @flip_coordinate_system.setter
    def flip_coordinate_system(self, value : bool) -> None:
        '''Flip the coordinate system, this is true by default'''
        raise NotImplementedError()
    

class ColladaTransformStyle:
    '''The node\'s transformation style of node'''
    
    COMPONENTS : ColladaTransformStyle
    '''Export the node\'s transformation as rotate/scale/translate'''
    MATRIX : ColladaTransformStyle
    '''Export the node\'s transfromation as matrix'''

class DracoCompressionLevel:
    '''Compression level for draco file'''
    
    NO_COMPRESSION : DracoCompressionLevel
    '''No compression, this will result in the minimum encoding time.'''
    FAST : DracoCompressionLevel
    '''Encoder will perform a compression as quickly as possible.'''
    STANDARD : DracoCompressionLevel
    '''Standard mode, with good compression and speed.'''
    OPTIMAL : DracoCompressionLevel
    '''Encoder will compress the scene optimally, which may takes longer time to finish.'''

class GltfEmbeddedImageFormat:
    '''How glTF exporter will embed the textures during the exporting.'''
    
    NO_CHANGE : GltfEmbeddedImageFormat
    '''Do not convert the image and keep it as it is.'''
    JPEG : GltfEmbeddedImageFormat
    '''All non-supported images formats will be converted to jpeg if possible.'''
    PNG : GltfEmbeddedImageFormat
    '''All non-supported images formats will be converted to png if possible.'''

class PdfLightingScheme:
    '''LightingScheme specifies the lighting to apply to 3D artwork.'''
    
    ARTWORK : PdfLightingScheme
    '''Uses the lights defined in the scene'''
    NONE : PdfLightingScheme
    '''No lights are used.'''
    WHITE : PdfLightingScheme
    '''Three blue-grey infinite lights, no ambient term'''
    DAY : PdfLightingScheme
    '''Three light-grey infinite lights, no ambient term'''
    NIGHT : PdfLightingScheme
    '''One yellow, one aqua, and one blue infinite light, no ambient term'''
    HARD : PdfLightingScheme
    '''Three grey infinite lights, moderate ambient term'''
    PRIMARY : PdfLightingScheme
    '''One red, one green, and one blue infinite light, no ambient term'''
    BLUE : PdfLightingScheme
    '''Three blue infinite lights, no ambient term'''
    RED : PdfLightingScheme
    '''Three red infinite lights, no ambient term'''
    CUBE : PdfLightingScheme
    '''Six grey infinite lights aligned with the major axes, no ambient term'''
    CAD : PdfLightingScheme
    '''Three grey infinite lights and one light attached to the camera, no ambient term'''
    HEADLAMP : PdfLightingScheme
    '''Single infinite light attached to the camera, low ambient term'''

class PdfRenderMode:
    '''Render mode specifies the style in which the 3D artwork is rendered.'''
    
    SOLID : PdfRenderMode
    '''Displays textured and lit geometric shapes.'''
    SOLID_WIREFRAME : PdfRenderMode
    '''Displays textured and lit geometric shapes (triangles) with single color edges on top of them.'''
    TRANSPARENT : PdfRenderMode
    '''Displays textured and lit geometric shapes (triangles) with an added level of transparency.'''
    TRANSPARENT_WIREFRAME : PdfRenderMode
    '''Displays textured and lit geometric shapes (triangles) with an added level of transparency, with single color opaque edges on top of it.'''
    BOUNDING_BOX : PdfRenderMode
    '''Displays the bounding box edges of each node, aligned with the axes of the local coordinate space for that node.'''
    TRANSPARENT_BOUNDING_BOX : PdfRenderMode
    '''Displays bounding boxes faces of each node, aligned with the axes of the local coordinate space for that node, with an added level of transparency.'''
    TRANSPARENT_BOUNDING_BOX_OUTLINE : PdfRenderMode
    '''Displays bounding boxes edges and faces of each node, aligned with the axes of the local coordinate space for that node, with an added level of transparency.'''
    WIREFRAME : PdfRenderMode
    '''Displays only edges in a single color.'''
    SHADED_WIREFRAME : PdfRenderMode
    '''Displays only edges, though interpolates their color between their two vertices and applies lighting.'''
    HIDDEN_WIREFRAME : PdfRenderMode
    '''Displays edges in a single color, though removes back-facing and obscured edges.'''
    VERTICES : PdfRenderMode
    '''Displays only vertices in a single color.'''
    SHADED_VERTICES : PdfRenderMode
    '''Displays only vertices, though uses their vertex color and applies lighting.'''
    ILLUSTRATION : PdfRenderMode
    '''Displays silhouette edges with surfaces, removes obscured lines.'''
    SOLID_OUTLINE : PdfRenderMode
    '''Displays silhouette edges with lit and textured surfaces, removes obscured lines.'''
    SHADED_ILLUSTRATION : PdfRenderMode
    '''Displays silhouette edges with lit and textured surfaces and an additional emissive term to remove poorly lit areas of the artwork.'''

