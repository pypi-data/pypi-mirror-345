#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This module hooks IAT and EAT to monitor all external functions calls,
#    very useful for [malware] reverse and debugging.
#    Copyright (C) 2025  Win32Hooking

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

'''
This module hooks IAT and EAT to monitor all external functions calls,
very useful for [malware] reverse and debugging.
'''

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = '''
This module hooks IAT and EAT to monitor all external functions calls,
very useful for [malware] reverse and debugging.
'''
__url__ = "https://github.com/mauricelambert/Win32Hooking"

# __all__ = []

__license__ = "GPL-3.0 License"
__copyright__ = '''
Win32Hooking  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
'''
copyright = __copyright__
license = __license__

print(copyright)

from ctypes import (
    windll,
    WinError,
    Structure,
    CFUNCTYPE,
    POINTER,
    memmove,
    cast,
    byref,
    addressof,
    sizeof,
    get_last_error,
    c_size_t,
    c_void_p,
    c_byte,
    c_char,
    c_int,
    c_uint8,
    c_uint32,
    c_uint16,
    c_char_p,
)
from PyPeLoader import (
    IMAGE_DOS_HEADER,
    IMAGE_NT_HEADERS,
    IMAGE_FILE_HEADER,
    IMAGE_OPTIONAL_HEADER64,
    ImportFunction,
    load_headers,
    load_in_memory,
    load_imports,
    load_relocations,
)
from ctypes.wintypes import DWORD, HMODULE, MAX_PATH, HANDLE, BOOL
from typing import Iterator, Callable, Dict, Union, List
from sys import argv, executable, exit
from dataclasses import dataclass
from _io import _BufferedIOBase
from os import getpid

PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_READ = 0x20
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_FREE = 0x10000

IMAGE_DIRECTORY_ENTRY_EXPORT = 0
TH32CS_SNAPMODULE = 0x00000008


class MODULEENTRY32(Structure):
    """
    This class implements the Module Entry for
    CreateToolhelp32Snapshot return value.
    """

    _fields_ = [
        ("dwSize", DWORD),
        ("th32ModuleID", DWORD),
        ("th32ProcessID", DWORD),
        ("GlblcntUsage", DWORD),
        ("ProccntUsage", DWORD),
        ("modBaseAddr", POINTER(c_byte)),
        ("modBaseSize", DWORD),
        ("hModule", HMODULE),
        ("szModule", c_char * 256),
        ("szExePath", c_char * MAX_PATH),
    ]


class IMAGE_EXPORT_DIRECTORY(Structure):
    """
    This class implements the image export directory
    to access export functions.
    """

    _fields_ = [
        ("Characteristics", c_uint32),
        ("TimeDateStamp", c_uint32),
        ("MajorVersion", c_uint16),
        ("MinorVersion", c_uint16),
        ("Name", c_uint32),
        ("Base", c_uint32),
        ("NumberOfFunctions", c_uint32),
        ("NumberOfNames", c_uint32),
        ("AddressOfFunctions", c_uint32),  # RVA to DWORD array
        ("AddressOfNames", c_uint32),  # RVA to RVA array (function names)
        ("AddressOfNameOrdinals", c_uint32),  # RVA to WORD array
    ]


class MEMORY_BASIC_INFORMATION(Structure):
    """
    This class implements the structure to get memory information.
    """

    _fields_ = [
        ("BaseAddress", c_void_p),
        ("AllocationBase", c_void_p),
        ("AllocationProtect", DWORD),
        ("RegionSize", c_size_t),
        ("State", DWORD),
        ("Protect", DWORD),
        ("Type", DWORD),
    ]


@dataclass
class Function:
    module: MODULEENTRY32
    module_name: str
    name: str
    address: int
    rva: int
    export_address: int
    index: int
    hook: Callable = None


generic_callback = CFUNCTYPE(c_void_p, *([c_void_p] * 67))

kernel32 = windll.kernel32

CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.argtypes = [DWORD, DWORD]
CreateToolhelp32Snapshot.restype = HANDLE

Module32First = kernel32.Module32First
Module32First.argtypes = [HANDLE, POINTER(MODULEENTRY32)]
Module32First.restype = BOOL

Module32Next = kernel32.Module32Next
Module32Next.argtypes = [HANDLE, POINTER(MODULEENTRY32)]
Module32Next.restype = BOOL

CloseHandle = kernel32.CloseHandle

VirtualProtect = kernel32.VirtualProtect
VirtualProtect.argtypes = [c_void_p, c_size_t, DWORD, POINTER(DWORD)]
VirtualProtect.restype = BOOL

reserved_hooks_space: Dict[str, int] = {}


def generic_callback_generator(
    type_: str, function: Union[Function, ImportFunction]
) -> Callable:
    """
    This function makes the specific callback for each function
    using the generic callback.
    """

    @generic_callback
    def callback(*arguments):
        print(type_, "call", function.module_name, function.name)
        answer = None
        while answer not in ("b", "c", "e"):
            answer = input(
                "Enter [b] for breakpoint, [c] to continue and [e] to exit: "
            )

        if answer == "b":
            breakpoint()
        elif answer == "e":
            exit(1)

        function_pointer = generic_callback(function.address)
        return_value = function_pointer(*arguments)
        print(type_, "return", function.module_name, function.name)
        return return_value

    return callback


def find_free_executable_region(
    start_address: int, function_number: int, max_scan=0x10000000
) -> int:
    """
    This function implements checks on memory to get a good address to
    allocate hooks jumps.
    """

    mbi = MEMORY_BASIC_INFORMATION()
    size_needed = function_number * 12
    current = start_address
    step = 0x100000

    while current < start_address + max_scan:
        result = kernel32.VirtualQuery(
            c_void_p(current), byref(mbi), sizeof(mbi)
        )

        if result == 0:
            break

        if mbi.State == MEM_FREE:
            alloc = kernel32.VirtualAlloc(
                c_void_p(current),
                c_size_t(size_needed),
                MEM_RESERVE | MEM_COMMIT,
                PAGE_EXECUTE_READ,
            )

            if alloc:
                return alloc

        current += step

    return 0


def generate_absolute_jump(address: int) -> bytes:
    """
    This function generates absolute JUMP.
    """

    mov_rax = b"\x48\xb8" + address.to_bytes(8, byteorder="little")
    jmp_rax = b"\xff\xe0"
    return mov_rax + jmp_rax


def write_in_memory(address: int, data: bytes) -> None:
    """
    This function writes data at specified memory with permissions management.
    """

    size = len(data)
    old_protect = DWORD()

    if not VirtualProtect(address, size, PAGE_READWRITE, byref(old_protect)):
        raise WinError()

    memmove(address, c_char_p(data), size)

    if not VirtualProtect(address, size, old_protect.value, byref(DWORD())):
        raise WinError()


def hook_function(function: Function) -> None:
    """
    This function hooks the function send as argument.
    """

    print("Hook", function.module_name, function.name)
    module_base = addressof(function.module.modBaseAddr.contents)
    real_value = cast(
        function.export_address, POINTER(c_uint32)
    ).contents.value

    if (
        hook_jump_address := reserved_hooks_space.get(function.module_name)
    ) is None:
        hook_jump_address = find_free_executable_region(
            addressof(function.module.modBaseAddr.contents)
            + function.module.modBaseSize,
            function.module.export_directory.NumberOfFunctions,
        )
        reserved_hooks_space[function.module_name] = hook_jump_address

    function.hook = generic_callback_generator("EAT", function)
    hook_pointer = cast(function.hook, c_void_p).value
    jump_instructions = generate_absolute_jump(hook_pointer)

    hook_jump_address += 12 * function.index
    hook_rva = hook_jump_address - module_base

    write_in_memory(
        function.export_address, hook_rva.to_bytes(4, byteorder="little")
    )
    write_in_memory(hook_jump_address, jump_instructions)
    hook_value = cast(
        function.export_address, POINTER(c_uint32)
    ).contents.value
    resolved_address = kernel32.GetProcAddress(
        module_base, function.name.encode()
    )

    print(
        "Hook",
        function.module_name,
        function.name,
        hex(real_value),
        hex(hook_value),
        hex(hook_rva),
        hex(hook_jump_address),
        hex(resolved_address),
    )


def rva_to_addr(base: int, rva: int) -> POINTER:
    """
    This function returns a pointer from a RVA.
    """

    return cast(base + rva, POINTER(c_uint8))


def rva_to_struct(base: int, rva: int, struct_type: Structure) -> Structure:
    """
    This function returns the structure instance from RVA.
    """

    return cast(base + rva, POINTER(struct_type)).contents


def list_exports(module: MODULEENTRY32) -> Iterator[Function]:
    """
    This function returns exported functions.
    """

    module_base = addressof(module.modBaseAddr.contents)
    dos = cast(module_base, POINTER(IMAGE_DOS_HEADER)).contents

    if dos.e_magic != 0x5A4D:
        raise ValueError("Invalid DOS header magic")

    nt_headers_address = module_base + dos.e_lfanew
    nt_headers = cast(nt_headers_address, POINTER(IMAGE_NT_HEADERS)).contents

    if nt_headers.Signature != 0x00004550:
        raise ValueError("Invalid PE signature")

    if nt_headers.FileHeader.Machine == 0x014C:
        optional_header = nt_headers.OptionalHeader
    elif nt_headers.FileHeader.Machine == 0x8664:
        optional_header = cast(
            nt_headers_address + 4 + sizeof(IMAGE_FILE_HEADER),
            POINTER(IMAGE_OPTIONAL_HEADER64),
        ).contents
    else:
        raise ValueError("Invalid Machine value NT File Headers")

    export_dirrectory_rva = optional_header.DataDirectory[
        IMAGE_DIRECTORY_ENTRY_EXPORT
    ].VirtualAddress

    if export_dirrectory_rva == 0:
        return None

    module.export_directory = export_directory = rva_to_struct(
        module_base, export_dirrectory_rva, IMAGE_EXPORT_DIRECTORY
    )

    base_export_functions_addresses = (
        module_base + export_directory.AddressOfFunctions
    )
    addresses_of_names = cast(
        module_base + export_directory.AddressOfNames,
        POINTER(c_uint32 * export_directory.NumberOfNames),
    ).contents
    addresses_of_functions = cast(
        base_export_functions_addresses,
        POINTER(c_uint32 * export_directory.NumberOfFunctions),
    ).contents
    addresses_of_ordinals = cast(
        module_base + export_directory.AddressOfNameOrdinals,
        POINTER(c_uint16 * export_directory.NumberOfNames),
    ).contents

    for i in range(export_directory.NumberOfNames):
        name_rva = addresses_of_names[i]
        ordinal = addresses_of_ordinals[i]
        function_rva = addresses_of_functions[ordinal]

        name_ptr = cast(module_base + name_rva, c_char_p)
        function_addr = module_base + function_rva

        yield Function(
            module,
            module.szModule.decode(),
            name_ptr.value.decode(),
            function_addr,
            function_rva,
            base_export_functions_addresses + ordinal * 4,
            i,
        )


def list_modules() -> Iterator[MODULEENTRY32]:
    """
    This generator yields the base address for each module.
    """

    pid = getpid()
    handle_snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid)
    if handle_snapshot == HANDLE(-1).value:
        raise WinError(get_last_error())

    module_entry = MODULEENTRY32()
    module_entry.dwSize = sizeof(MODULEENTRY32)

    success = Module32First(handle_snapshot, byref(module_entry))
    if not success:
        CloseHandle(handle_snapshot)
        raise WinError(get_last_error())

    while success:
        base_addr = addressof(module_entry.modBaseAddr.contents)
        yield module_entry
        success = Module32Next(handle_snapshot, byref(module_entry))

    CloseHandle(handle_snapshot)


def hooks_EAT() -> Dict[str, Function]:
    """
    This function hooks the EAT (Export Address Table) functions.
    """

    functions = {}

    for module in list_modules():
        for function in list_exports(module):
            functions[
                str(addressof(function.module.modBaseAddr.contents))
                + "|"
                + function.name
            ] = function
            # if function.rva != cast(function.export_address, POINTER(c_uint32)).contents.value:
            #     print(function)
            hook_function(function)

    return functions


def hooks_IAT(imports: List[ImportFunction]) -> Dict[str, ImportFunction]:
    """
    This function hooks the IAT (Import Address Table) functions.
    """

    functions = {}

    for function in imports:
        functions[f"{function.module}|{function.name}"] = function
        function.hook = generic_callback_generator("IAT", function)
        hook_pointer = cast(function.hook, c_void_p).value
        write_in_memory(
            function.import_address,
            hook_pointer.to_bytes(sizeof(c_void_p), byteorder="little"),
        )

    return functions


def load(file: _BufferedIOBase) -> None:
    """
    This function is based on: https://github.com/mauricelambert/PyPeLoader/blob/af116589d379220b7c886fffc146cc7dd7b91732/PyPeLoader.py#L628

    This function does all steps to load, hooks functions (EAT and IAT) and
    execute the PE program in memory.
    """

    pe_headers = load_headers(file)
    image_base = load_in_memory(file, pe_headers)
    file.close()

    imports = load_imports(pe_headers, image_base)
    import_hooks = hooks_IAT(imports)
    export_hooks = hooks_EAT()
    load_relocations(pe_headers, image_base)

    function_type = CFUNCTYPE(c_int)
    function = function_type(
        image_base + pe_headers.optional.AddressOfEntryPoint
    )
    function()


def main() -> int:
    """
    This function is based on: https://github.com/mauricelambert/PyPeLoader/blob/af116589d379220b7c886fffc146cc7dd7b91732/PyPeLoader.py#L647

    This function is the main function to start the script
    from the command line.
    """

    if len(argv) <= 1:
        print(
            'USAGES: "',
            executable,
            '" "',
            argv[0],
            '" executable_path',
            sep="",
        )
        return 1

    load(open(argv[1], "rb"))
    return 0


if __name__ == "__main__":
    exit(main())
