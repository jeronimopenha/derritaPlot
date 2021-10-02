import argparse
import os
import sys
import traceback

from veriloggen import *

p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not p in sys.path:
    sys.path.insert(0, p)


def create_args():
    parser = argparse.ArgumentParser('derrita_plot_creator -h')
    parser.add_argument('-i', '--grn_file_input', help='GRN file to be used in circuit creator', type=str)
    parser.add_argument('-b', '--bit_width', help='Bit quantity for counters', type=int, default=32)
    parser.add_argument('-n', '--project_name', help='Project name', type=str, default='a.prj')
    parser.add_argument('-o', '--project_output_path', help='Project location', type=str, default='.')
    return parser.parse_args()


def create_project(hpcgra_root, arch_json, name, output_path):
    pass
    #cgra = Cgra(arch_json)
    #cgraacc = CgraAccelerator(cgra)
    #acc_axi = AccAXIInterface(cgraacc)

    #template_path = hpcgra_root + '/resources/template.prj'
    #cmd = 'cp -r %s  %s/%s' % (template_path, output_path, name)
    #commands_getoutput(cmd)

    #hw_path = '%s/%s/xilinx_aws_f1/hw/' % (output_path, name)
    #sw_path = '%s/%s/xilinx_aws_f1/sw/' % (output_path, name)

    #m = acc_axi.create_kernel_top(name)
    #m.to_verilog(hw_path + 'src/%s.v' % (name))

    #num_axis_str = 'NUM_M_AXIS=%d' % cgraacc.get_num_in()
    #conn_str = acc_axi.get_connectivity_config(name)

    #write_file(hw_path + 'simulate/num_m_axis.mk', num_axis_str)
    #write_file(hw_path + 'synthesis/num_m_axis.mk', num_axis_str)
    #write_file(sw_path + 'host/prj_name', name)
    #write_file(hw_path + 'simulate/prj_name', name)
    #write_file(hw_path + 'synthesis/prj_name', name)
    #write_file(hw_path + 'simulate/vitis_config.txt', conn_str)
    #write_file(hw_path + 'synthesis/vitis_config.txt', conn_str)


def main():
    args = create_args()
    running_path = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.getcwd() + '/../'

    if args.output == '.':
        args.output = running_path

    if args.json:

        args.json = running_path + '/' + args.json

        # create_project(project_root, args.json, args.name, args.output)

        print('Project successfully created in %s/%s' % (args.output, args.name))
    else:
        msg = 'Missing parameters. Run create_project -h to see all parameters needed'

        raise Exception(msg)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        traceback.print_exc()
