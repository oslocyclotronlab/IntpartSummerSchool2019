# Export nlds & gsfs to TALYS

Here we give an example on how to convert *arbirary* nld and gsf to fileformats readable by talys [as of October 2019] & how to use them. Thanks to Ann-Cecilie @cecgresonant for helping me in compiling this information.

- Use `convert_talys` to convert your nuclear level density and gsf to file formats readable
  by talys.
- The gsf files can be loaded using the `E1file` and `M1file` keywords in TALYS. Remember to
  set `gnorm` to one, otherwise they will be renormalized. An examples if you want to use
  the gsf of `240Pu` (e.g. in `239Pu + n`).
  ```
  # Gamma strength: tables for the E1 and M1 components
  E1file 94 240 path/to/gsfE1.dat
  M1file 94 240 path/to/gsfM1.dat
  gnorm 1.
  ```
- If you don't have values for the gsf above a certain energy `Estop`, the
  script provided here will extrapolate the values above `Estop` up to 30 MeV
  (needed by talys). So don't trust (n,g) [...] calculations with `En > Estop
  Sn`. If you want to have calcs for higher energies, extend the input table).

- For the nlds, you it will be a bit more *hacky*:
  - Find the nld file for your nucleus, somewhere like
    `/talys/structure/density/ground/goriely/Pu.tab`. Make a backup of it.
  - Exchange *the section* of the table for the final nucleus of interest with the section in
    `nld_totalys.txt`. Note further that:
    - The total format of the table has to be uncanged: It needs to have the
      same number of excitations energies (->#rows) and Js (#-> columns). If
      you create a table up to 10 MeV, only replace the section up to 10 MeV.
    - If you replace the seciton only up to `Estop = 10 MeV`, remember that you will use
      the default NLD values for `Ex > 10 MeV`. You can only trust (n,g)
      calculations up to `En = Estop - Sn`. (If you want to have calcs for higher
      energies, extend the input table).

  - To use them in talys, select `ldmode 4` (corresponds to the `goriely` folder) **and**
    specify explicity, that these number shall not be changed with `ptable` and `ctable`:
    ```
    ldmodel 4
    ptable 94 240 0.0
    ctable 94 240 0.0

    ```
  - Remember to use a number of levels that matches with the nld you input before
    In the example data, the nld was just given down to ~1.3 MeV, as we use(d) discrete
    levels below. One could state to use the first, say 10 levels (arb. choice in the text
    here)
    ```
    Nlevels 94 240 10
    ```
- Finally, you should always make sure that all formats were read correctly. I don't exactly
  recall which of these keywords you need, but you might just as well use all of them
  ```
  outbasic y
  outomp y
  outlevels y
  outdensity y
  outgamma y
  ```
    - Check summary information like `D0` and `<Gg>`. Start with `D0`: If you level density is read incorrectly, this value wil not be right.

    - Then you might want to copy out and plot the nld and gsfs that talys uses. It's in the output file somewhere like. Check whether the output says *Level density per parity*. If so, to get the total NLD for plotting, multiply it by 2.
      ```

      Level density parameters for Z= 94 N=146 (240Pu)

      [...]

      Level density per parity for ground state
      (Total level density also per parity)

        Ex     a    sigma   total   JP=  0.0  JP=  1.0  JP=  2.0  JP=  3.0  JP=  4.0  JP=  5.0  JP=  6.0  JP=  7.0  JP=  8.0

       0.25               6.200E+00 2.400E-01 6.650E-01 9.500E-01 1.050E+00 9.900E-01 8.150E-01 6.050E-01 4.025E-01 2.440E-01
       0.50               1.115E+01 2.835E-01 8.100E-01 1.215E+00 1.460E+00 1.530E+00 1.450E+00 1.260E+00 1.015E+00 7.650E-01
       0.75               2.010E+01 4.115E-01 1.185E+00 1.820E+00 2.250E+00 2.455E+00 2.440E+00 2.255E+00 1.950E+00 1.590E+00
       [...]
       ```

     - and the gsf (now in units of 1/MeV^3 again, not mb/MeV). To convert, use
       `factor_from_mb = 8.6737E-08   # const. factor in mb^(-1) MeV^(-2)` [or use the plotting from `convert_talys.py` which will do it for you].

      ```
       ########## GAMMA STRENGTH FUNCTIONS, [...]##########
         [...]
           E       f(M1)        f(E1)        T(M1)        T(E1)

         0.001  0.00000E+00  9.90827E-09  0.00000E+00  6.22555E-17
         0.002  6.38737E-12  9.94197E-09  3.21064E-19  4.99738E-16
         0.005  1.59686E-11  9.99423E-09  1.25417E-17  7.84945E-15
         0.010  3.19380E-11  1.00813E-08  2.00673E-16  6.33429E-14
         0.020  6.38832E-11  1.02555E-08  3.21112E-15  5.15500E-13
         [...]
       ```

      There was a bug in some versions of talys 1.9. *If* the `f(E1)` column is filled with zeros, replace `gammapar.f` in the talys folder with the one provided here in `data/` and recompile.
