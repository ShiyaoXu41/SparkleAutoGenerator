@echo off


@REM @REM generate vmod directly
call python vmod_gen\top_gen.py
call python vmod_gen\prefixsum_gen.py
call python vmod_gen\pe_group_gen.py
call python vmod_gen\fan_ctrl_gen.py
call python vmod_gen\fan_network_gen.py
call python vmod_gen\adder_switch_gen.py
call python vmod_gen\middle_reduct_gen.py
call python vmod_gen\final_reduct_gen.py
call python vmod_gen\multi_fan_ctrl_gen.py
call python vmod_gen\multi_fan_network_gen.py
call python vmod_gen\results_accum_gen.py

@REM @REM generate vmod by replacing
call python vmod_gen\load_MK_gen.py
call python vmod_gen\load_KN_gen.py
call python vmod_gen\buff_KN_gen.py
call python vmod_gen\mult_switch_gen.py
call python vmod_gen\res_output_gen.py


@REM @REM generate tb directly
call python tb_gen\tb_top_gen.py
call python tb_gen\tb_res_gen.py
call python tb_gen\tb_peg_gen.py
call python tb_gen\tb_mid_gen.py
call python tb_gen\tb_load_MK_gen.py
call python tb_gen\tb_load_KN_gen.py
call python tb_gen\tb_fin_gen.py
call python tb_gen\tb_buff_gen.py


@REM copy sim files
call python sim\sim_bat.py

@REM generate sim data
call python sim\MK_data_gen.py
call python sim\KN_data_gen.py


@REM copy parameters&decfunc py files
call python bat.py


pause


@REM ===== 2 tcl ===== 
@REM bram_MK_bitmap
@REM bram_MK_pointer
@REM bram_MK_data
@REM fifo_MK_data
@REM fifo_dest
@REM fifo_vn
@REM fifo_flag

@REM bram_KN_data
@REM fifo_KN_data

@REM fifo_KN_data_backup

@REM Mult

@REM Adder

@REM fifo_output