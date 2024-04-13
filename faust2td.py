import json
import re
import math
import argparse
import os
from os.path import isfile, isdir, abspath
import subprocess
import shlex
import platform


def parse_ui(items, labels=[]) -> None:
    global ui_leaf_items
    for item in items:
        if 'address' in item:
            if drop_prefix and len(labels):
                labels = labels[1:]
            labels.append(item['label'])
            item['label'] = '/'.join(labels)
            ui_leaf_items.append(item)
        if 'items' in item:
            labels.append(item['label'])
            parse_ui(item['items'], labels=labels)


def item_to_td_parname(item) -> str:
    address = item['address']
    if address.startswith('/'):
        address = address[1:]

    address = address.split('/')
    if len(address) > 1 and drop_prefix:
        address = address[1:]
    address = '/'.join(address)

    address = re.sub('[^a-zA-Z0-9]', '', address)

    address = address[0].upper() + address[1:].lower()

    return address


def add_par_double(item) -> str:
    parname = item_to_td_parname(item)
    label = item['label'].replace('"', '\\"')
    init = item['init']
    min_val = item['min']
    max_val = item['max']
    text = f"""
{{
    OP_NumericParameter np;

    np.name = "{parname}";
    np.label = "{label}";
    np.defaultValues[0] = {init};
    np.minSliders[0] = np.minValues[0] = {min_val};
    np.maxSliders[0] = np.maxValues[0] = {max_val};
    np.clampMins[0] = np.clampMaxes[0] = true;

    OP_ParAppendResult res = manager->appendFloat(np);
    assert(res == OP_ParAppendResult::Success);
}}"""
    return text


def legalName(text) -> str:
    # todo: do what the official tdu python module does.
    text = text.replace(' ', '_')
    return text


def add_nentry(item) -> str:
    parname = item_to_td_parname(item)
    label = item['label'].replace('"', '\\"')
    init = item['init']
    theMin = item['min']
    theMax = item['max']
    step = item['step']

    numItems = math.floor((theMax - theMin) / step) + 1

    items = [min((theMin + step * i), theMax) for i in range(numItems)]
    n = len(items)

    names = labels = [str(i) for i in items]

    for meta in (item['meta'] if 'meta' in item else []):
        if 'style' in meta:
            style = meta['style']

            if 'menu' in style and item['type'] == 'nentry':
                # style might be "menu{'Noise':0;'Sawtooth':1}"
                """
                import("stdfaust.lib");
                s = nentry("Signal[style:menu{'Noise':0;'Sawtooth':1}]",0,0,1,1);
                process = select2(s,no.noise,os.sawtooth(440)) * .01 <: _, _;
                """
                # https://github.com/Fr0stbyteR/faust-ui/blob/5da18109241d9c0d44974c9afac402809a3c2995/src/components/Group.ts#L27
                reg = re.compile(r"(?:(?:'|_)(.+?)(?:'|_):([-+]?[0-9]*\.?[0-9]+?))")
                matches = reg.findall(style)
                # matches == [('Noise', '0'), ('Sawtooth', '1'), ('Triangle', '2')]
                names = [legalName(pair[0]) for pair in matches]
                labels = [pair[0] for pair in matches]

    names = ",".join([f'"{name}"' for name in names])
    labels = ",".join([f'"{label}"' for label in labels])

    text = f"""
{{
    OP_StringParameter	sp;

    sp.name = "{parname}";
    sp.label = "{label}";

    sp.defaultValue = "{init}";

    const char *names[] = {{{names}}};
    const char *labels[] = {{{labels}}};

    OP_ParAppendResult res = manager->appendMenu(sp, {n}, names, labels);
    assert(res == OP_ParAppendResult::Success);
}}"""
    return text


def add_toggle(item) -> str:

    parname = item_to_td_parname(item)
    label = item['label'].replace('"', '\\"')

    text = f"""
{{
    OP_NumericParameter np;

    np.name = "{parname}";
    np.label = "{label}";

    OP_ParAppendResult res = manager->appendToggle(np);
    assert(res == OP_ParAppendResult::Success);
}}"""
    return text


def get_libfaust_dir():
    cmake_build_arch = f"-DCMAKE_OSX_ARCHITECTURES=x86_64"

    if platform.system() == 'Windows':
        subprocess.run(shlex.split("python download_libfaust.py"), check=True, cwd="thirdparty/libfaust")
        libfaust_dir = 'thirdparty/libfaust/win64/Release'
    else:
        subprocess.run(shlex.split("python3 download_libfaust.py"), check=True, cwd="thirdparty/libfaust")
        arch = args.arch
        if arch == 'arm64':
            libfaust_dir = 'thirdparty/libfaust/darwin-arm64/Release'
            cmake_build_arch = f"-DCMAKE_OSX_ARCHITECTURES=arm64"
        elif arch == 'x86_64':
            libfaust_dir = 'thirdparty/libfaust/darwin-x64/Release'
            cmake_build_arch = f"-DCMAKE_OSX_ARCHITECTURES=x86_64"
        else:
            raise RuntimeError(f"Unknown CPU architecture: {arch}.")

    libfaust_dir = str(abspath(libfaust_dir))

    if platform.system() == 'Windows':
        assert isdir(libfaust_dir), "Have you run `call download_libfaust.bat`?"
    else:
        assert isdir(libfaust_dir), "Have you run `sh download_libfaust.sh`?"
    
    return libfaust_dir, cmake_build_arch


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dsp', required=True, help="The path (relative or absolute) to a text file containing Faust DSP code.")
    parser.add_argument('--type', required=True, help='The unique name for this CHOP. It must start with a '
                        'capital A-Z character, and all the following characters must lower case or numbers (a-z, 0-9)')
    parser.add_argument('--label', required=True, help='The text that will show up in the OP Create Dialog.')
    parser.add_argument('--icon', required=True, help="This should be three letters (upper or lower case), or numbers, which"
                        " are used to create an icon for this Custom OP.")
    parser.add_argument('--author', required=False, default='', help="The author's name.")
    parser.add_argument('--email', required=False, default='', help="The author's email")
    parser.add_argument('--drop-prefix', required=False, action='store_true', default=False,
                        help="Automatically drop the first group name to make the CHOP's parameter names shorter.")
    parser.add_argument("--arch", default=platform.machine(), help="CPU Architecture for which to build.")

    args = parser.parse_args()

    op_type = args.type # {OP_TYPE}
    op_label = args.label # {OP_LABEL}
    op_icon = args.icon  # {OP_ICON}
    author_name = args.author # {AUTHOR_NAME}
    author_email = args.email # {AUTHOR_EMAIL}
    drop_prefix = args.drop_prefix

    op_type = re.sub('[^a-zA-Z0-9]', '', op_type)
    op_type = op_type[0].upper() + op_type[1:].lower()

    op_icon = re.sub('[^a-zA-Z0-9]', '', op_icon)

    assert len(op_icon) == 3, "The OP icon must be three letters or numbers."

    dsp_file = args.dsp
    assert isfile(dsp_file), f'The requested DSP file "{dsp_file}" was not found.'

    libfaust_dir, cmake_build_arch = get_libfaust_dir()

    # Turn the Faust code into C++ code:
    faust_script = f'faust -i "{dsp_file}" -lang cpp -cn FaustDSP -json -a faust2touchdesigner/template_faustaudio.h -o faust2touchdesigner/{op_type}.h'
    
    try:
        print(f'Executing faust script:\n{faust_script}')
        subprocess.call(shlex.split(faust_script))
    except FileNotFoundError as e:
        # Maybe `faust` isn't in PATH, so default to trying the libfaust binary.
        faust_script = f'{libfaust_dir}/bin/' + faust_script
        print(f'Executing faust script:\n{faust_script}')
        subprocess.call(shlex.split(faust_script))

    assert isfile(f'faust2touchdesigner/{op_type}.h')

    json_file = dsp_file + '.json'
    assert isfile(json_file), f"The JSON file wasn't found at {json_file}"

    with open(json_file, 'r') as f:
        text = f.readlines()

        # hacky thing to fix invalid json
        text = '\n'.join([line for line in text if '"library_list":' not in line and '"include_pathnames":' not in line])

        j = json.loads(text)

    # input widget types are ones which will need custom parameters on a Base COMP.
    INPUT_WIDGET_TYPES = ['button', 'checkbox', 'nentry', 'hslider', 'vslider']
    OUTPUT_WIDGET_TYPES = ['hbargraph', 'vbargraph']
    GROUP_WIDGET_TYPES = ['hgroup', 'vgroup', 'tgroup']

    ui_leaf_items = []

    parse_ui(j['ui'])

    # remove duplicate addresses
    addresses = set()
    ui_leaf_items_copy = []
    for item in ui_leaf_items:
        if item['address'] not in addresses:
            addresses.add(item['address'])
            ui_leaf_items_copy.append(item)

    ui_leaf_items = ui_leaf_items_copy
    del ui_leaf_items_copy

    set_par_values = []

    for item in ui_leaf_items:
        address = item['address']
        parname = item_to_td_parname(item)
        widgettype = item['type']
        if widgettype in ['hslider', 'vslider']:
            set_par_values.append(f'm_ui.setParamValue("{address}", inputs->getParDouble("{parname}"));')
        elif widgettype in ['checkbox', 'button']:
            set_par_values.append(f'm_ui.setParamValue("{address}", inputs->getParInt("{parname}"));')
        elif widgettype == 'nentry':
            set_par_values.append(f'm_ui.setParamValue("{address}", inputs->getParInt("{parname}"));')
        elif widgettype in OUTPUT_WIDGET_TYPES:
            pass
        else:
            raise ValueError(f"Unknown widget type: {widgettype}")

    set_par_values = '\n'.join(set_par_values)

    setup_parameters = []

    for item in ui_leaf_items:
        widgettype = item['type']
        if widgettype in ['hslider', 'vslider']:
            setup_parameters.append(add_par_double(item))
        elif widgettype == 'button':
            setup_parameters.append(add_toggle(item))
        elif widgettype == 'checkbox':
            setup_parameters.append(add_toggle(item))
        elif widgettype == 'nentry':
            setup_parameters.append(add_nentry(item))
        elif widgettype in OUTPUT_WIDGET_TYPES:
            # todo: automatically build a UI for the user?
            pass
        else:
            raise ValueError(f"Unkown ui widget type: {widgettype}")

    setup_parameters = '\n'.join(setup_parameters)

    with open('faust2touchdesigner/template_FaustCHOP.h', 'r') as f:
        template = f.read()
    template = template.replace('{OP_TYPE}', op_type)
    with open(f'faust2touchdesigner/Faust_{op_type}_CHOP.h', 'w') as f:
        f.write(template)  

    with open('faust2touchdesigner/template_FaustCHOP.cpp', 'r') as f:
        template = f.read()

    template = template.replace('{OP_TYPE}', op_type)
    template = template.replace('{OP_LABEL}', op_label)
    template = template.replace('{OP_ICON}', op_icon)
    template = template.replace('{AUTHOR_NAME}', author_name)
    template = template.replace('{AUTHOR_EMAIL}', author_email)
    template = template.replace('{SET_PAR_VALUES}', set_par_values)
    template = template.replace('{SETUP_PARAMETERS}', setup_parameters)

    with open(f'faust2touchdesigner/Faust_{op_type}_CHOP.cpp', 'w') as f:
        f.write(template)

    cmake_osx_deployment_target = f"-DCMAKE_OSX_DEPLOYMENT_TARGET=12.0"

    # execute CMake and build
    build_dir = f'build_{op_type}'
    generator = " -G Xcode " if platform.system() == 'Darwin' else ''
    subprocess.call(shlex.split(f'cmake faust2touchdesigner -B{build_dir} {generator} -DOP_TYPE={op_type} -DAUTHOR_NAME="{author_name}" -DLIBFAUST_DIR="{libfaust_dir}" {cmake_osx_deployment_target} {cmake_build_arch}'))
    subprocess.call(shlex.split(f'cmake --build {build_dir} --config Release'))

    if platform.system() == 'Darwin':
        file_dest = f'"{build_dir}/Release/{op_type}.plugin"'
        subprocess.call(shlex.split(f'cp -r {file_dest} Plugins'))

    print('All done!')
