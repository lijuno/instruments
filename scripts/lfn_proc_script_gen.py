# This script generate the Matlab script for processing LFN data

import glob
import re


def bias_mapping(bias_level):
    """
    Map the bias level on SR570 to real-world values (unit: V)
    Return a float type
    """

    bias_dict = {-2000: -1.961,
                 -1900: -1.863,
                 -1800: -1.767,
                 -1700: -1.668,
                 -1600: -1.570,
                 -1500: -1.471,
                 -1400: -1.373,
                 -1300: -1.275,
                 -1200: -1.177,
                 -1100: -1.080,
                 -1000: -0.981,
                 -900: -0.883,
                 -800: -0.785,
                 -700: -0.686,
                 -600: -0.588,
                 -500: -0.489,
                 -400: -0.391,
                 -300: -0.294,
                 -200: -0.196,
                 -100: -0.097,
                 50: 0.051,
                 100: 0.100,
                 150: 0.149,
                 200: 0.199,
                 250: 0.248,
                 300: 0.298,
                 350: 0.346,
                 400: 0.395,
                 450: 0.445,
                 500: 0.494,
                 550: 0.543,
                 600: 0.593,
                 650: 0.642,
                 700: 0.692,
                 750: 0.741,
                 800: 0.790,
                 850: 0.840,
                 900: 0.889,
                 950: 0.939,
                 1000: 0.988}
    if bias_level in bias_dict.keys():
        return bias_dict[bias_level]
    else:
        raise ValueError('Unrecognized bias level')


def get_param_list(df_list):
    """
    Return an int type array containing bias level (on SR570), and a float type array containing gainitivity values
    """
    bias_list = []
    gain_list = []
    for s in df_list:
        # s should something like 'Vbias-600_gain1e-6.dat'
        # Extract the number after 'Vbias'
        fn = re.sub('.dat', '', s)     # remove extension name '.dat'
        name_list = fn.split('_')     # separate information with separator '_'
        bias_level = 0
        gain = 0  # initialize
        for n in name_list:
            if 'Vbias' in n:
                bias_level = int(re.sub('Vbias', '', n))
            elif 'gain' in n:
                gain = float(re.sub('gain', '', n))
        if bias_level == 0:
            raise RuntimeError("Input filename %s doesn't contain the string 'Vbias' " % s)
        elif gain == 0:
            raise RuntimeError("Input filename %s doesn't contain the string 'gain' " % s)
        bias_list.append(bias_level)
        gain_list.append(gain)
    return bias_list, gain_list


def make_gain_str(gain):
    """
    Take a numerical gain and format it to a string (for the use of variable naming)
    Return a string type
    """
    gstr = '%.1e' % gain
    gstr = re.sub('\+', '',  gstr)
    gstr = re.sub('\.', 'p', gstr)
    gstr = re.sub('-', 'neg', gstr)
    return gstr

def get_varlist(df_list, var_prefix):
    """
    Return a string array containing FFT output, Idc, alpha, dalpha, or S_I0 variable names
    """
    var_list = []
    bias_list, gain_list = get_param_list(df_list)

    for ii in range(bias_list.__len__()):
        if bias_list[ii] >= 0:
            v = '%s_bias%d_gain%s' % (var_prefix, bias_list[ii], make_gain_str(gain_list[ii]))
        elif bias_list[ii] <0:
            v = '%s_biasn%d_gain%s' % (var_prefix, -bias_list[ii], make_gain_str(gain_list[ii]))
        var_list.append(v)
    return var_list


def get_gain(df):
    """
    Get gain values from the data file name
    Input: data file name, a string
    Return: gain (unit: V/A), float type
    """
    fn = re.sub('.dat', '', df)
    name_list = fn.split('_')
    gain = 0   # Initialize
    for n in name_list:
        if 'gain' in n:
            gain = float(re.sub('gain', '', n))
    if gain == 0:
        raise RuntimeError('Cannot find the gain value from the filename %s' % df)
    return gain


if __name__ == '__main__':

    # Get raw data file list excluding the 'fft_' files
    datafile_list = glob.glob('*.dat')  # list the data file in the current directory
    datafile_list2= []
    for s in datafile_list:
        if 'fft' in s:
            pass
        else:
            datafile_list2.append(s)
    # Now datafile_list2 contains only the raw data

    # Get gain value
    gain = get_gain(datafile_list2[0])

    output_filename = 'plot_data.m'
    f = open(output_filename, 'w')
    #f.write('gain = 1e-6;  \n\n')  # may need to change this to adjust amplifier gain
    f.write('f0 = 10; \nf_fitting_range = [10, 1000]; \n')
    f.write("fs = 50e3; \nN_avg = 500; \nratio_overlap = 0.8;\n\n")
    f.write("IV=importdata('IV.txt');\n")


    # Don't need to change anything below
    # FFT processing
    nd = len(datafile_list2)
    bias_list, gain_list = get_param_list(datafile_list2)
    fft_varlist = get_varlist(datafile_list2, 'fft')   # generate the variables for FFT results in Matlab
    dc_varlist = get_varlist(datafile_list2, 'Idc')
    alpha_varlist = get_varlist(datafile_list2, 'alpha')
    dalpha_varlist = get_varlist(datafile_list2, 'dalpha')
    SI0_varlist = get_varlist(datafile_list2, 'SI0')

    for ii in range(nd):
        f.write("[%s, f] = fft_pro('%s', fs, N_avg, ratio_overlap); \n"
                % (fft_varlist[ii], datafile_list2[ii]))

    f.write('\n')
    f.write('% Convert to current power density \n')
    for ii in range(nd):
        f.write('%s = %s / %s^2; \n'
                % (fft_varlist[ii], fft_varlist[ii], gain_list[ii]))

    f.write('\n')
    for ii in range(nd):
        f.write('[%s, %s, %s] = flicker_calc(f, %s, f0, f_fitting_range); \n' %
                (alpha_varlist[ii], SI0_varlist[ii], dalpha_varlist[ii], fft_varlist[ii]))

    f.write('\n')
    for ii in range(nd):
        f.write('%s = interp1(IV(:,1), IV(:,2), %.3f); \n'
                % (dc_varlist[ii], bias_mapping(bias_list[ii])))
    f.write('\n')

    f.write('Idc_list = [')
    for ii in range(nd):
        f.write('%s ' % dc_varlist[ii])
    f.write(']; \n')

    f.write('alpha_list = [')
    for ii in range(nd):
        f.write('%s ' % alpha_varlist[ii])
    f.write(']; \n')

    f.write('dalpha_list = [')
    for ii in range(nd):
        f.write('%s ' % dalpha_varlist[ii])
    f.write(']; \n')

    f.write('SI0_list = [')
    for ii in range(nd):
        f.write('%s ' % SI0_varlist[ii])
    f.write(']; \n\n')

    # Plot
    f.write('% Plotting \n')
    f.write('figure(1) \nloglog(')
    for ii in range(nd):
        if ii < nd-1:
            f.write('f, %s, ... \n' % (fft_varlist[ii]))
        elif ii == nd-1:
            f.write('f, %s) \n' % (fft_varlist[ii]))
    f.write("legend(")
    for ii in range(nd):
        if ii < nd-1:
            f.write("'%.3f V', " % bias_mapping(bias_list[ii]))
        elif ii == nd-1:
            f.write("'%.3f V'" % bias_mapping(bias_list[ii]))
    f.write(") \n\n")

    f.write("[Idc_list2, IX] = sort(Idc_list);\n")
    f.write('figure(2) \n')
    f.write("plot(Idc_list(IX), alpha_list(IX), 'o-')\n")
    f.write("title('Idc VS alpha')\n\n")

    f.write('figure(3) \n')
    f.write("loglog(abs(Idc_list(IX)), SI0_list(IX), 'o-') \n")
    f.write("title('Idc VS S_{I0}')\n\n")

    f.close()