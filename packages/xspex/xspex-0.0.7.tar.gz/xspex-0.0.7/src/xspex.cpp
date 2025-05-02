#include "xspex.hpp"

#define STRINGIFY_HELPER(x) #x
#define STRINGIFY(x) STRINGIFY_HELPER(x)

using namespace pybind11::literals;

py::dict xla_registrations() {
    py::dict reg;
    // Add the models, auto-generated from the model.dat file.

    // float
    reg["agauss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_agauss, 2>);
    reg["agnsed_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<agnsed_, 15>);
    reg["agnslim_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<agnslim_, 14>);
    reg["apec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_apec, 3>);
    reg["bapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bapec, 4>);
    reg["bcempow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bcempow, 7>);
    reg["bcheb6_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bcheb6, 11>);
    reg["bcie_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bcie, 5>);
    reg["bcoolflow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bcoolflow, 6>);
    reg["bcph_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bcph, 5>);
    reg["bequil_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bequil, 4>);
    reg["bexpcheb6_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bexpcheb6, 11>);
    reg["bgadem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bgaussDem, 7>);
    reg["bgnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bgnei, 6>);
    reg["bnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bnei, 5>);
    reg["bsnapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bsnapec, 7>);
    reg["btapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_btapec, 5>);
    reg["bbody_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsblbd_, 1>);
    reg["bbodyrad_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsbbrd_, 1>);
    reg["bexrav_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xsbexrav, 9>);
    reg["bexriv_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xsbexriv, 11>);
    reg["bknpower_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_brokenPowerLaw, 3>);
    reg["bkn2pow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_broken2PowerLaw, 5>);
    reg["bmc_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsbmc_, 3>);
    reg["bnpshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bnpshock, 7>);
    reg["bpshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bpshock, 6>);
    reg["bremss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsbrms_, 1>);
    reg["brnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_brnei, 6>);
    reg["bsedov_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bsedov, 6>);
    reg["bvapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvapec, 16>);
    reg["bvcempow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvcempow, 20>);
    reg["bvcheb6_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvcheb6, 24>);
    reg["bvcie_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvcie, 17>);
    reg["bvcoolflow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvcoolflow, 19>);
    reg["bvcph_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvcph, 18>);
    reg["bvequil_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvequil, 15>);
    reg["bvexpcheb6_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvexpcheb6, 24>);
    reg["bvgadem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvgaussDem, 20>);
    reg["bvgnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvgnei, 18>);
    reg["bvnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvnei, 17>);
    reg["bvnpshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvnpshock, 19>);
    reg["bvpshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvpshock, 18>);
    reg["bvrnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvrnei, 18>);
    reg["bvsedov_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvsedov, 18>);
    reg["bvtapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvtapec, 17>);
    reg["bvvapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvvapec, 33>);
    reg["bvvcie_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvvcie, 34>);
    reg["bvvgadem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvvgaussDem, 36>);
    reg["bvvgnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvvgnei, 35>);
    reg["bvvnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvvnei, 34>);
    reg["bvvnpshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvvnpshock, 36>);
    reg["bvvpshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvvpshock, 35>);
    reg["bvvrnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvvrnei, 35>);
    reg["bvvsedov_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvvsedov, 35>);
    reg["bvvtapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvvtapec, 34>);
    reg["bvvwdem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvvwDem, 37>);
    reg["bvwdem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bvwDem, 21>);
    reg["bwdem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_bwDem, 8>);
    reg["c6mekl_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_c6mekl, 10>);
    reg["c6pmekl_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_c6pmekl, 10>);
    reg["c6pvmkl_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_c6pvmkl, 23>);
    reg["c6vmekl_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_c6vmekl, 23>);
    reg["carbatm_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_carbatm, 3>);
    reg["cemekl_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_cemMekal, 6>);
    reg["cempow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_cempow, 6>);
    reg["cevmkl_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_cemVMekal, 19>);
    reg["cflow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xscflw, 5>);
    reg["cheb6_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_cheb6, 10>);
    reg["cie_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_cie, 4>);
    reg["compbb_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<compbb_, 3>);
    reg["compmag_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<xscompmag, 8>);
    reg["compls_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<compls_, 2>);
    reg["compps_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xscompps, 19>);
    reg["compst_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<compst_, 2>);
    reg["comptb_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<xscomptb, 6>);
    reg["compth_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xscompth, 20>);
    reg["comptt_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xstitg_, 5>);
    reg["coolflow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_coolflow, 5>);
    reg["cph_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_cph, 4>);
    reg["cplinear_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_cplinear, 20>);
    reg["cutoffpl_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_cutoffPowerLaw, 2>);
    reg["disk_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<disk_, 3>);
    reg["diskir_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<diskir_, 8>);
    reg["diskbb_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsdskb_, 1>);
    reg["diskline_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_diskline, 5>);
    reg["diskm_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<diskm_, 4>);
    reg["disko_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<disko_, 4>);
    reg["diskpbb_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<diskpbb_, 2>);
    reg["diskpn_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsdiskpn_, 2>);
    reg["eebremss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_eebremss, 3>);
    reg["eplogpar_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<eplogpar_, 2>);
    reg["eqpair_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xseqpair, 20>);
    reg["eqtherm_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xseqth, 20>);
    reg["equil_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_equil, 3>);
    reg["expdec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsxpdec_, 1>);
    reg["expcheb6_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_expcheb6, 10>);
    reg["ezdiskbb_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<ezdiskbb_, 1>);
    reg["feklor_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_FeKfromSevenLorentzians, 0>);
    reg["gauss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_gaussianLine, 2>);
    reg["gadem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_gaussDem, 6>);
    reg["gnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_gnei, 5>);
    reg["grad_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<grad_, 6>);
    reg["grbcomp_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<xsgrbcomp, 9>);
    reg["grbjet_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<xsgrbjet, 13>);
    reg["grbm_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsgrbm_, 3>);
    reg["hatm_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_hatm, 3>);
    reg["jet_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<jet_, 15>);
    reg["kerrbb_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_kerrbb, 9>);
    reg["kerrd_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_kerrd, 7>);
    reg["kerrdisk_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_spin, 9>);
    reg["kyconv_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_f_XLA_f32<kyconv_, 12>);
    reg["kyrline_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<kyrline_, 11>);
    reg["laor_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_laor, 5>);
    reg["laor2_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_laor2, 7>);
    reg["logpar_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_logpar, 3>);
    reg["lorentz_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_lorentzianLine, 2>);
    reg["meka_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_meka, 4>);
    reg["mekal_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_mekal, 5>);
    reg["mkcflow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xsmkcf, 5>);
    reg["nei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_nei, 4>);
    reg["nlapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_nlapec, 3>);
    reg["npshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_npshock, 6>);
    reg["nsa_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<nsa_, 4>);
    reg["nsagrav_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<nsagrav_, 3>);
    reg["nsatmos_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<nsatmos_, 4>);
    reg["nsmax_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_nsmax, 3>);
    reg["nsmaxg_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_nsmaxg, 5>);
    reg["nsx_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_nsx, 5>);
    reg["nteea_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xsnteea, 15>);
    reg["nthcomp_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_nthcomp, 5>);
    reg["optxagn_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<optxagn_, 13>);
    reg["optxagnf_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<optxagnf_, 11>);
    reg["pegpwrlw_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xspegp_, 3>);
    reg["pexmon_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<pexmon_, 7>);
    reg["pexrav_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xspexrav, 7>);
    reg["pexriv_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xspexriv, 9>);
    reg["plcabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsp1tr_, 10>);
    reg["powerlaw_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_powerLaw, 1>);
    reg["posm_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsposm_, 0>);
    reg["pshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_pshock, 5>);
    reg["qsosed_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<qsosed_, 6>);
    reg["raymond_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_raysmith, 3>);
    reg["redge_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xredge_, 2>);
    reg["refsch_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsrefsch_, 13>);
    reg["rgsext_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_rgsExtendedSource, 2>);
    reg["rgsxsrc_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_rgsxsrc, 1>);
    reg["rnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_rnei, 5>);
    reg["sedov_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_sedov, 5>);
    reg["sirf_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_sirf, 9>);
    reg["slimbh_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<slimbbmodel, 9>);
    reg["smaug_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<xsmaug, 22>);
    reg["snapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_snapec, 6>);
    reg["srcut_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<srcut_, 2>);
    reg["sresc_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<sresc_, 2>);
    reg["ssa_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<ssa_, 2>);
    reg["sssed_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<sssed_, 14>);
    reg["step_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsstep_, 2>);
    reg["tapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_tapec, 4>);
    reg["vagauss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vagauss, 2>);
    reg["vapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vapec, 15>);
    reg["vbremss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsbrmv_, 2>);
    reg["vcempow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vcempow, 19>);
    reg["vcheb6_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vcheb6, 23>);
    reg["vcie_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vcie, 16>);
    reg["vcoolflow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vcoolflow, 18>);
    reg["vcph_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vcph, 17>);
    reg["vexpcheb6_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vexpcheb6, 23>);
    reg["vequil_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vequil, 14>);
    reg["vgadem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vgaussDem, 19>);
    reg["vgauss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vgaussianLine, 2>);
    reg["vgnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vgnei, 17>);
    reg["vlorentz_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vlorentzianLine, 2>);
    reg["vmeka_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vmeka, 17>);
    reg["vmekal_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vmekal, 18>);
    reg["vmcflow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xsvmcf, 18>);
    reg["vnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vnei, 16>);
    reg["vnpshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vnpshock, 18>);
    reg["voigt_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_voigtLine, 3>);
    reg["vpshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vpshock, 17>);
    reg["vraymond_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vraysmith, 14>);
    reg["vrnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vrnei, 17>);
    reg["vsedov_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vsedov, 17>);
    reg["vtapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vtapec, 16>);
    reg["vvapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvapec, 32>);
    reg["vvcie_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvcie, 33>);
    reg["vvgadem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvgaussDem, 35>);
    reg["vvgnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvgnei, 34>);
    reg["vvnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvnei, 33>);
    reg["vvnpshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvnpshock, 35>);
    reg["vvoigt_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvoigtLine, 3>);
    reg["vvpshock_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvpshock, 34>);
    reg["vvrnei_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvrnei, 34>);
    reg["vvsedov_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvsedov, 34>);
    reg["vvtapec_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvtapec, 33>);
    reg["vvwdem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvwDem, 36>);
    reg["vwdem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vwDem, 20>);
    reg["wdem_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_wDem, 7>);
    reg["zagauss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zagauss, 3>);
    reg["zbbody_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszbod_, 2>);
    reg["zbknpower_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zBrokenPowerLaw, 4>);
    reg["zbremss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszbrm_, 2>);
    reg["zcutoffpl_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zcutoffPowerLaw, 3>);
    reg["zfeklor_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zFeKfromSevenLorentzians, 1>);
    reg["zgauss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xszgau, 3>);
    reg["zkerrbb_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zkerrbb, 9>);
    reg["zlogpar_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zLogpar, 4>);
    reg["zlorentz_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zlorentzianLine, 3>);
    reg["zpowerlw_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zpowerLaw, 2>);
    reg["zvlorentz_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zvlorentzianLine, 3>);
    reg["zvoigt_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zvoigtLine, 4>);
    reg["zvvoigt_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zvvoigtLine, 4>);
    reg["absori_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xsabsori, 6>);
    reg["acisabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_acisabs, 8>);
    reg["constant_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xscnst_, 1>);
    reg["cabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xscabs_, 1>);
    reg["cyclabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xscycl_, 5>);
    reg["dust_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsdust_, 2>);
    reg["edge_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsedge_, 2>);
    reg["expabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsabsc_, 1>);
    reg["expfac_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsexp_, 3>);
    reg["gabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_gaussianAbsorptionLine, 3>);
    reg["heilin_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsphei_, 3>);
    reg["highecut_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xshecu_, 2>);
    reg["hrefl_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xshrfl_, 8>);
    reg["ismabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_F_XLA_f32<ismabs_, 31>);
    reg["ismdust_f32"] = xspex::EncapsulateFunction(xspex::wrapper_F_XLA_f32<ismdust_, 3>);
    reg["logconst_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_logconst, 1>);
    reg["log10con_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_log10con, 1>);
    reg["lorabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_lorentzianAbsorptionLine, 3>);
    reg["lyman_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xslyman_, 4>);
    reg["notch_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsntch_, 3>);
    reg["olivineabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_F_XLA_f32<olivineabs_, 2>);
    reg["pcfabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsabsp_, 2>);
    reg["phabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsphab_, 1>);
    reg["plabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsplab_, 2>);
    reg["polconst_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_polconst, 2>);
    reg["pollin_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_pollin, 4>);
    reg["polpow_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_polpow, 4>);
    reg["pwab_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xspwab, 3>);
    reg["redden_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xscred_, 1>);
    reg["smedge_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xssmdg_, 4>);
    reg["spexpcut_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_superExpCutoff, 2>);
    reg["spline_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsspln_, 6>);
    reg["sssice_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xssssi_, 1>);
    reg["swind1_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_swind1, 4>);
    reg["tbabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_tbabs, 1>);
    reg["tbfeo_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_tbfeo, 4>);
    reg["tbgas_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_tbgas, 2>);
    reg["tbgrain_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_tbgrain, 6>);
    reg["tbvarabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_tbvabs, 42>);
    reg["tbpcf_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_tbpcf, 3>);
    reg["tbrel_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_tbrel, 42>);
    reg["uvred_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsred_, 1>);
    reg["varabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsabsv_, 18>);
    reg["vgabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vgaussianAbsorptionLine, 3>);
    reg["vlorabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vlorentzianAbsorptionLine, 3>);
    reg["voigtabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_voigtAbsorptionLine, 4>);
    reg["vphabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsvphb_, 18>);
    reg["vvoigtabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_vvoigtAbsorptionLine, 4>);
    reg["wabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsabsw_, 1>);
    reg["wndabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xswnab_, 2>);
    reg["xion_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xsxirf_, 13>);
    reg["xscat_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_xscatmodel, 4>);
    reg["zbabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<xszbabs, 4>);
    reg["zdust_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<mszdst_, 4>);
    reg["zedge_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszedg_, 3>);
    reg["zgabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zgaussianAbsorptionLine, 4>);
    reg["zhighect_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszhcu_, 3>);
    reg["zigm_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<zigm_, 3>);
    reg["zlorabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zlorentzianAbsorptionLine, 4>);
    reg["zpcfabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszabp_, 3>);
    reg["zphabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszphb_, 2>);
    reg["zvlorabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zvlorentzianAbsorptionLine, 4>);
    reg["zvoigtabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zvoigtAbsorptionLine, 5>);
    reg["zvvoigtabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zvvoigtAbsorptionLine, 5>);
    reg["zxipab_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<zxipab_, 5>);
    reg["zxipcf_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zxipcf, 4>);
    reg["zredden_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszcrd_, 2>);
    reg["zsmdust_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<msldst_, 4>);
    reg["ztbabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_ztbabs, 2>);
    reg["zvagauss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zvagauss, 3>);
    reg["zvarabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszvab_, 19>);
    reg["zvfeabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszvfe_, 5>);
    reg["zvgabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zvgaussianAbsorptionLine, 4>);
    reg["zvgauss_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<C_zvgaussianLine, 3>);
    reg["zvphabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszvph_, 19>);
    reg["zwabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszabs_, 2>);
    reg["zwndabs_f32"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f32<xszwnb_, 3>);
    reg["cflux_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_cflux, 3>);
    reg["clumin_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_clumin, 4>);
    reg["cglumin_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_cglumin, 4>);
    reg["cpflux_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_cpflux, 3>);
    reg["gsmooth_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_gsmooth, 2>);
    reg["ireflect_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_ireflct, 7>);
    reg["kdblur_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_kdblur, 4>);
    reg["kdblur2_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_kdblur2, 6>);
    reg["kerrconv_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_spinconv, 7>);
    reg["lsmooth_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_lsmooth, 2>);
    reg["partcov_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_PartialCovering, 1>);
    reg["rdblur_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_rdblur, 4>);
    reg["reflect_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_reflct, 5>);
    reg["rfxconv_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_rfxconv, 5>);
    reg["simpl_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_simpl, 3>);
    reg["thcomp_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_f_XLA_f32<thcompf_, 4>);
    reg["vashift_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_vashift, 1>);
    reg["vmshift_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_vmshift, 1>);
    reg["xilconv_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_xilconv, 6>);
    reg["zashift_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_zashift, 1>);
    reg["zmshift_f32"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f32<C_zmshift, 1>);
    reg["bwcycl_f32"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f32<beckerwolff, 12>);

    // double
    reg["agauss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_agauss, 2>);
    reg["agnsed_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<agnsed_, 15>);
    reg["agnslim_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<agnslim_, 14>);
    reg["apec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_apec, 3>);
    reg["bapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bapec, 4>);
    reg["bcempow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bcempow, 7>);
    reg["bcheb6_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bcheb6, 11>);
    reg["bcie_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bcie, 5>);
    reg["bcoolflow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bcoolflow, 6>);
    reg["bcph_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bcph, 5>);
    reg["bequil_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bequil, 4>);
    reg["bexpcheb6_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bexpcheb6, 11>);
    reg["bgadem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bgaussDem, 7>);
    reg["bgnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bgnei, 6>);
    reg["bnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bnei, 5>);
    reg["bsnapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bsnapec, 7>);
    reg["btapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_btapec, 5>);
    reg["bbody_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsblbd_, 1>);
    reg["bbodyrad_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsbbrd_, 1>);
    reg["bexrav_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xsbexrav, 9>);
    reg["bexriv_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xsbexriv, 11>);
    reg["bknpower_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_brokenPowerLaw, 3>);
    reg["bkn2pow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_broken2PowerLaw, 5>);
    reg["bmc_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsbmc_, 3>);
    reg["bnpshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bnpshock, 7>);
    reg["bpshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bpshock, 6>);
    reg["bremss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsbrms_, 1>);
    reg["brnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_brnei, 6>);
    reg["bsedov_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bsedov, 6>);
    reg["bvapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvapec, 16>);
    reg["bvcempow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvcempow, 20>);
    reg["bvcheb6_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvcheb6, 24>);
    reg["bvcie_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvcie, 17>);
    reg["bvcoolflow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvcoolflow, 19>);
    reg["bvcph_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvcph, 18>);
    reg["bvequil_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvequil, 15>);
    reg["bvexpcheb6_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvexpcheb6, 24>);
    reg["bvgadem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvgaussDem, 20>);
    reg["bvgnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvgnei, 18>);
    reg["bvnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvnei, 17>);
    reg["bvnpshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvnpshock, 19>);
    reg["bvpshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvpshock, 18>);
    reg["bvrnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvrnei, 18>);
    reg["bvsedov_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvsedov, 18>);
    reg["bvtapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvtapec, 17>);
    reg["bvvapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvvapec, 33>);
    reg["bvvcie_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvvcie, 34>);
    reg["bvvgadem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvvgaussDem, 36>);
    reg["bvvgnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvvgnei, 35>);
    reg["bvvnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvvnei, 34>);
    reg["bvvnpshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvvnpshock, 36>);
    reg["bvvpshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvvpshock, 35>);
    reg["bvvrnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvvrnei, 35>);
    reg["bvvsedov_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvvsedov, 35>);
    reg["bvvtapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvvtapec, 34>);
    reg["bvvwdem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvvwDem, 37>);
    reg["bvwdem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bvwDem, 21>);
    reg["bwdem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_bwDem, 8>);
    reg["c6mekl_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_c6mekl, 10>);
    reg["c6pmekl_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_c6pmekl, 10>);
    reg["c6pvmkl_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_c6pvmkl, 23>);
    reg["c6vmekl_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_c6vmekl, 23>);
    reg["carbatm_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_carbatm, 3>);
    reg["cemekl_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_cemMekal, 6>);
    reg["cempow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_cempow, 6>);
    reg["cevmkl_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_cemVMekal, 19>);
    reg["cflow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xscflw, 5>);
    reg["cheb6_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_cheb6, 10>);
    reg["cie_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_cie, 4>);
    reg["compbb_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<compbb_, 3>);
    reg["compmag_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<xscompmag, 8>);
    reg["compls_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<compls_, 2>);
    reg["compps_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xscompps, 19>);
    reg["compst_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<compst_, 2>);
    reg["comptb_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<xscomptb, 6>);
    reg["compth_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xscompth, 20>);
    reg["comptt_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xstitg_, 5>);
    reg["coolflow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_coolflow, 5>);
    reg["cph_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_cph, 4>);
    reg["cplinear_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_cplinear, 20>);
    reg["cutoffpl_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_cutoffPowerLaw, 2>);
    reg["disk_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<disk_, 3>);
    reg["diskir_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<diskir_, 8>);
    reg["diskbb_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsdskb_, 1>);
    reg["diskline_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_diskline, 5>);
    reg["diskm_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<diskm_, 4>);
    reg["disko_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<disko_, 4>);
    reg["diskpbb_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<diskpbb_, 2>);
    reg["diskpn_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsdiskpn_, 2>);
    reg["eebremss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_eebremss, 3>);
    reg["eplogpar_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<eplogpar_, 2>);
    reg["eqpair_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xseqpair, 20>);
    reg["eqtherm_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xseqth, 20>);
    reg["equil_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_equil, 3>);
    reg["expdec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsxpdec_, 1>);
    reg["expcheb6_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_expcheb6, 10>);
    reg["ezdiskbb_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<ezdiskbb_, 1>);
    reg["feklor_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_FeKfromSevenLorentzians, 0>);
    reg["gauss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_gaussianLine, 2>);
    reg["gadem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_gaussDem, 6>);
    reg["gnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_gnei, 5>);
    reg["grad_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<grad_, 6>);
    reg["grbcomp_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<xsgrbcomp, 9>);
    reg["grbjet_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<xsgrbjet, 13>);
    reg["grbm_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsgrbm_, 3>);
    reg["hatm_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_hatm, 3>);
    reg["jet_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<jet_, 15>);
    reg["kerrbb_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_kerrbb, 9>);
    reg["kerrd_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_kerrd, 7>);
    reg["kerrdisk_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_spin, 9>);
    reg["kyconv_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_f_XLA_f64<kyconv_, 12>);
    reg["kyrline_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<kyrline_, 11>);
    reg["laor_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_laor, 5>);
    reg["laor2_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_laor2, 7>);
    reg["logpar_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_logpar, 3>);
    reg["lorentz_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_lorentzianLine, 2>);
    reg["meka_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_meka, 4>);
    reg["mekal_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_mekal, 5>);
    reg["mkcflow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xsmkcf, 5>);
    reg["nei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_nei, 4>);
    reg["nlapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_nlapec, 3>);
    reg["npshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_npshock, 6>);
    reg["nsa_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<nsa_, 4>);
    reg["nsagrav_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<nsagrav_, 3>);
    reg["nsatmos_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<nsatmos_, 4>);
    reg["nsmax_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_nsmax, 3>);
    reg["nsmaxg_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_nsmaxg, 5>);
    reg["nsx_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_nsx, 5>);
    reg["nteea_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xsnteea, 15>);
    reg["nthcomp_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_nthcomp, 5>);
    reg["optxagn_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<optxagn_, 13>);
    reg["optxagnf_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<optxagnf_, 11>);
    reg["pegpwrlw_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xspegp_, 3>);
    reg["pexmon_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<pexmon_, 7>);
    reg["pexrav_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xspexrav, 7>);
    reg["pexriv_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xspexriv, 9>);
    reg["plcabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsp1tr_, 10>);
    reg["powerlaw_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_powerLaw, 1>);
    reg["posm_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsposm_, 0>);
    reg["pshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_pshock, 5>);
    reg["qsosed_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<qsosed_, 6>);
    reg["raymond_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_raysmith, 3>);
    reg["redge_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xredge_, 2>);
    reg["refsch_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsrefsch_, 13>);
    reg["rgsext_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_rgsExtendedSource, 2>);
    reg["rgsxsrc_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_rgsxsrc, 1>);
    reg["rnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_rnei, 5>);
    reg["sedov_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_sedov, 5>);
    reg["sirf_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_sirf, 9>);
    reg["slimbh_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<slimbbmodel, 9>);
    reg["smaug_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<xsmaug, 22>);
    reg["snapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_snapec, 6>);
    reg["srcut_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<srcut_, 2>);
    reg["sresc_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<sresc_, 2>);
    reg["ssa_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<ssa_, 2>);
    reg["sssed_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<sssed_, 14>);
    reg["step_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsstep_, 2>);
    reg["tapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_tapec, 4>);
    reg["vagauss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vagauss, 2>);
    reg["vapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vapec, 15>);
    reg["vbremss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsbrmv_, 2>);
    reg["vcempow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vcempow, 19>);
    reg["vcheb6_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vcheb6, 23>);
    reg["vcie_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vcie, 16>);
    reg["vcoolflow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vcoolflow, 18>);
    reg["vcph_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vcph, 17>);
    reg["vexpcheb6_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vexpcheb6, 23>);
    reg["vequil_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vequil, 14>);
    reg["vgadem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vgaussDem, 19>);
    reg["vgauss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vgaussianLine, 2>);
    reg["vgnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vgnei, 17>);
    reg["vlorentz_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vlorentzianLine, 2>);
    reg["vmeka_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vmeka, 17>);
    reg["vmekal_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vmekal, 18>);
    reg["vmcflow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xsvmcf, 18>);
    reg["vnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vnei, 16>);
    reg["vnpshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vnpshock, 18>);
    reg["voigt_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_voigtLine, 3>);
    reg["vpshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vpshock, 17>);
    reg["vraymond_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vraysmith, 14>);
    reg["vrnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vrnei, 17>);
    reg["vsedov_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vsedov, 17>);
    reg["vtapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vtapec, 16>);
    reg["vvapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvapec, 32>);
    reg["vvcie_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvcie, 33>);
    reg["vvgadem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvgaussDem, 35>);
    reg["vvgnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvgnei, 34>);
    reg["vvnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvnei, 33>);
    reg["vvnpshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvnpshock, 35>);
    reg["vvoigt_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvoigtLine, 3>);
    reg["vvpshock_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvpshock, 34>);
    reg["vvrnei_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvrnei, 34>);
    reg["vvsedov_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvsedov, 34>);
    reg["vvtapec_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvtapec, 33>);
    reg["vvwdem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvwDem, 36>);
    reg["vwdem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vwDem, 20>);
    reg["wdem_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_wDem, 7>);
    reg["zagauss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zagauss, 3>);
    reg["zbbody_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszbod_, 2>);
    reg["zbknpower_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zBrokenPowerLaw, 4>);
    reg["zbremss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszbrm_, 2>);
    reg["zcutoffpl_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zcutoffPowerLaw, 3>);
    reg["zfeklor_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zFeKfromSevenLorentzians, 1>);
    reg["zgauss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xszgau, 3>);
    reg["zkerrbb_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zkerrbb, 9>);
    reg["zlogpar_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zLogpar, 4>);
    reg["zlorentz_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zlorentzianLine, 3>);
    reg["zpowerlw_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zpowerLaw, 2>);
    reg["zvlorentz_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zvlorentzianLine, 3>);
    reg["zvoigt_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zvoigtLine, 4>);
    reg["zvvoigt_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zvvoigtLine, 4>);
    reg["absori_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xsabsori, 6>);
    reg["acisabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_acisabs, 8>);
    reg["constant_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xscnst_, 1>);
    reg["cabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xscabs_, 1>);
    reg["cyclabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xscycl_, 5>);
    reg["dust_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsdust_, 2>);
    reg["edge_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsedge_, 2>);
    reg["expabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsabsc_, 1>);
    reg["expfac_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsexp_, 3>);
    reg["gabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_gaussianAbsorptionLine, 3>);
    reg["heilin_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsphei_, 3>);
    reg["highecut_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xshecu_, 2>);
    reg["hrefl_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xshrfl_, 8>);
    reg["ismabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_F_XLA_f64<ismabs_, 31>);
    reg["ismdust_f64"] = xspex::EncapsulateFunction(xspex::wrapper_F_XLA_f64<ismdust_, 3>);
    reg["logconst_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_logconst, 1>);
    reg["log10con_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_log10con, 1>);
    reg["lorabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_lorentzianAbsorptionLine, 3>);
    reg["lyman_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xslyman_, 4>);
    reg["notch_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsntch_, 3>);
    reg["olivineabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_F_XLA_f64<olivineabs_, 2>);
    reg["pcfabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsabsp_, 2>);
    reg["phabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsphab_, 1>);
    reg["plabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsplab_, 2>);
    reg["polconst_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_polconst, 2>);
    reg["pollin_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_pollin, 4>);
    reg["polpow_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_polpow, 4>);
    reg["pwab_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xspwab, 3>);
    reg["redden_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xscred_, 1>);
    reg["smedge_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xssmdg_, 4>);
    reg["spexpcut_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_superExpCutoff, 2>);
    reg["spline_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsspln_, 6>);
    reg["sssice_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xssssi_, 1>);
    reg["swind1_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_swind1, 4>);
    reg["tbabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_tbabs, 1>);
    reg["tbfeo_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_tbfeo, 4>);
    reg["tbgas_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_tbgas, 2>);
    reg["tbgrain_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_tbgrain, 6>);
    reg["tbvarabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_tbvabs, 42>);
    reg["tbpcf_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_tbpcf, 3>);
    reg["tbrel_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_tbrel, 42>);
    reg["uvred_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsred_, 1>);
    reg["varabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsabsv_, 18>);
    reg["vgabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vgaussianAbsorptionLine, 3>);
    reg["vlorabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vlorentzianAbsorptionLine, 3>);
    reg["voigtabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_voigtAbsorptionLine, 4>);
    reg["vphabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsvphb_, 18>);
    reg["vvoigtabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_vvoigtAbsorptionLine, 4>);
    reg["wabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsabsw_, 1>);
    reg["wndabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xswnab_, 2>);
    reg["xion_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xsxirf_, 13>);
    reg["xscat_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_xscatmodel, 4>);
    reg["zbabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<xszbabs, 4>);
    reg["zdust_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<mszdst_, 4>);
    reg["zedge_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszedg_, 3>);
    reg["zgabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zgaussianAbsorptionLine, 4>);
    reg["zhighect_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszhcu_, 3>);
    reg["zigm_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<zigm_, 3>);
    reg["zlorabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zlorentzianAbsorptionLine, 4>);
    reg["zpcfabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszabp_, 3>);
    reg["zphabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszphb_, 2>);
    reg["zvlorabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zvlorentzianAbsorptionLine, 4>);
    reg["zvoigtabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zvoigtAbsorptionLine, 5>);
    reg["zvvoigtabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zvvoigtAbsorptionLine, 5>);
    reg["zxipab_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<zxipab_, 5>);
    reg["zxipcf_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zxipcf, 4>);
    reg["zredden_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszcrd_, 2>);
    reg["zsmdust_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<msldst_, 4>);
    reg["ztbabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_ztbabs, 2>);
    reg["zvagauss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zvagauss, 3>);
    reg["zvarabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszvab_, 19>);
    reg["zvfeabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszvfe_, 5>);
    reg["zvgabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zvgaussianAbsorptionLine, 4>);
    reg["zvgauss_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<C_zvgaussianLine, 3>);
    reg["zvphabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszvph_, 19>);
    reg["zwabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszabs_, 2>);
    reg["zwndabs_f64"] = xspex::EncapsulateFunction(xspex::wrapper_f_XLA_f64<xszwnb_, 3>);
    reg["cflux_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_cflux, 3>);
    reg["clumin_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_clumin, 4>);
    reg["cglumin_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_cglumin, 4>);
    reg["cpflux_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_cpflux, 3>);
    reg["gsmooth_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_gsmooth, 2>);
    reg["ireflect_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_ireflct, 7>);
    reg["kdblur_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_kdblur, 4>);
    reg["kdblur2_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_kdblur2, 6>);
    reg["kerrconv_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_spinconv, 7>);
    reg["lsmooth_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_lsmooth, 2>);
    reg["partcov_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_PartialCovering, 1>);
    reg["rdblur_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_rdblur, 4>);
    reg["reflect_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_reflct, 5>);
    reg["rfxconv_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_rfxconv, 5>);
    reg["simpl_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_simpl, 3>);
    reg["thcomp_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_f_XLA_f64<thcompf_, 4>);
    reg["vashift_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_vashift, 1>);
    reg["vmshift_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_vmshift, 1>);
    reg["xilconv_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_xilconv, 6>);
    reg["zashift_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_zashift, 1>);
    reg["zmshift_f64"] = xspex::EncapsulateFunction(xspex::wrapper_con_C_XLA_f64<C_zmshift, 1>);
    reg["bwcycl_f64"] = xspex::EncapsulateFunction(xspex::wrapper_C_XLA_f64<beckerwolff, 12>);

    return reg;
}

PYBIND11_MODULE(_compiled, m) {
#ifdef XSPEX_VERSION
    m.attr("__version__") = STRINGIFY(XSPEX_VERSION);
#else
    m.attr("__version__") = "dev";
#endif
    m.doc() = R"doc(
Call Xspec models from Python
=============================

Part of codes are adapted from xspec-models-cxc, which is highly experimental.

The Xspec model library is automatically initialized on module loading.

Support routines
----------------
get_version - The version of the Xspec model library.
chatter - Get or set the Xspec chatter level.
abundance - Get or set the abundance-table setting.
cross_section - Get or set the cross-section-table setting.
element_abundance - Get the abundance for an element by name or atomic number.
element_name - Get the name of an element given the atomic number.
cosmology - Get or set the cosmology (H0, q0, lambda0) settings.

Table Models
------------
tableModel

Additive models
---------------
agauss - 2 parameters.
agnsed - 15 parameters.
agnslim - 14 parameters.
apec - 3 parameters.
bapec - 4 parameters.
bcempow - 7 parameters.
bcheb6 - 11 parameters.
bcie - 5 parameters.
bcoolflow - 6 parameters.
bcph - 5 parameters.
bequil - 4 parameters.
bexpcheb6 - 11 parameters.
bgadem - 7 parameters.
bgnei - 6 parameters.
bnei - 5 parameters.
bsnapec - 7 parameters.
btapec - 5 parameters.
bbody - 1 parameter.
bbodyrad - 1 parameter.
bexrav - 9 parameters.
bexriv - 11 parameters.
bknpower - 3 parameters.
bkn2pow - 5 parameters.
bmc - 3 parameters.
bnpshock - 7 parameters.
bpshock - 6 parameters.
bremss - 1 parameter.
brnei - 6 parameters.
bsedov - 6 parameters.
bvapec - 16 parameters.
bvcempow - 20 parameters.
bvcheb6 - 24 parameters.
bvcie - 17 parameters.
bvcoolflow - 19 parameters.
bvcph - 18 parameters.
bvequil - 15 parameters.
bvexpcheb6 - 24 parameters.
bvgadem - 20 parameters.
bvgnei - 18 parameters.
bvnei - 17 parameters.
bvnpshock - 19 parameters.
bvpshock - 18 parameters.
bvrnei - 18 parameters.
bvsedov - 18 parameters.
bvtapec - 17 parameters.
bvvapec - 33 parameters.
bvvcie - 34 parameters.
bvvgadem - 36 parameters.
bvvgnei - 35 parameters.
bvvnei - 34 parameters.
bvvnpshock - 36 parameters.
bvvpshock - 35 parameters.
bvvrnei - 35 parameters.
bvvsedov - 35 parameters.
bvvtapec - 34 parameters.
bvvwdem - 37 parameters.
bvwdem - 21 parameters.
bwdem - 8 parameters.
c6mekl - 10 parameters.
c6pmekl - 10 parameters.
c6pvmkl - 23 parameters.
c6vmekl - 23 parameters.
carbatm - 3 parameters.
cemekl - 6 parameters.
cempow - 6 parameters.
cevmkl - 19 parameters.
cflow - 5 parameters.
cheb6 - 10 parameters.
cie - 4 parameters.
compbb - 3 parameters.
compmag - 8 parameters.
compls - 2 parameters.
compps - 19 parameters.
compst - 2 parameters.
comptb - 6 parameters.
compth - 20 parameters.
comptt - 5 parameters.
coolflow - 5 parameters.
cph - 4 parameters.
cplinear - 20 parameters.
cutoffpl - 2 parameters.
disk - 3 parameters.
diskir - 8 parameters.
diskbb - 1 parameter.
diskline - 5 parameters.
diskm - 4 parameters.
disko - 4 parameters.
diskpbb - 2 parameters.
diskpn - 2 parameters.
eebremss - 3 parameters.
eplogpar - 2 parameters.
eqpair - 20 parameters.
eqtherm - 20 parameters.
equil - 3 parameters.
expdec - 1 parameter.
expcheb6 - 10 parameters.
ezdiskbb - 1 parameter.
feklor - no parameters.
gauss - 2 parameters.
gadem - 6 parameters.
gnei - 5 parameters.
grad - 6 parameters.
grbcomp - 9 parameters.
grbjet - 13 parameters.
grbm - 3 parameters.
hatm - 3 parameters.
jet - 15 parameters.
kerrbb - 9 parameters.
kerrd - 7 parameters.
kerrdisk - 9 parameters.
kyrline - 11 parameters.
laor - 5 parameters.
laor2 - 7 parameters.
logpar - 3 parameters.
lorentz - 2 parameters.
meka - 4 parameters.
mekal - 5 parameters.
mkcflow - 5 parameters.
nei - 4 parameters.
nlapec - 3 parameters.
npshock - 6 parameters.
nsa - 4 parameters.
nsagrav - 3 parameters.
nsatmos - 4 parameters.
nsmax - 3 parameters.
nsmaxg - 5 parameters.
nsx - 5 parameters.
nteea - 15 parameters.
nthcomp - 5 parameters.
optxagn - 13 parameters.
optxagnf - 11 parameters.
pegpwrlw - 3 parameters.
pexmon - 7 parameters.
pexrav - 7 parameters.
pexriv - 9 parameters.
plcabs - 10 parameters.
powerlaw - 1 parameter.
posm - no parameters.
pshock - 5 parameters.
qsosed - 6 parameters.
raymond - 3 parameters.
redge - 2 parameters.
refsch - 13 parameters.
rnei - 5 parameters.
sedov - 5 parameters.
sirf - 9 parameters.
slimbh - 9 parameters.
smaug - 22 parameters.
snapec - 6 parameters.
srcut - 2 parameters.
sresc - 2 parameters.
ssa - 2 parameters.
sssed - 14 parameters.
step - 2 parameters.
tapec - 4 parameters.
vagauss - 2 parameters.
vapec - 15 parameters.
vbremss - 2 parameters.
vcempow - 19 parameters.
vcheb6 - 23 parameters.
vcie - 16 parameters.
vcoolflow - 18 parameters.
vcph - 17 parameters.
vexpcheb6 - 23 parameters.
vequil - 14 parameters.
vgadem - 19 parameters.
vgauss - 2 parameters.
vgnei - 17 parameters.
vlorentz - 2 parameters.
vmeka - 17 parameters.
vmekal - 18 parameters.
vmcflow - 18 parameters.
vnei - 16 parameters.
vnpshock - 18 parameters.
voigt - 3 parameters.
vpshock - 17 parameters.
vraymond - 14 parameters.
vrnei - 17 parameters.
vsedov - 17 parameters.
vtapec - 16 parameters.
vvapec - 32 parameters.
vvcie - 33 parameters.
vvgadem - 35 parameters.
vvgnei - 34 parameters.
vvnei - 33 parameters.
vvnpshock - 35 parameters.
vvoigt - 3 parameters.
vvpshock - 34 parameters.
vvrnei - 34 parameters.
vvsedov - 34 parameters.
vvtapec - 33 parameters.
vvwdem - 36 parameters.
vwdem - 20 parameters.
wdem - 7 parameters.
zagauss - 3 parameters.
zbbody - 2 parameters.
zbknpower - 4 parameters.
zbremss - 2 parameters.
zcutoffpl - 3 parameters.
zfeklor - 1 parameter.
zgauss - 3 parameters.
zkerrbb - 9 parameters.
zlogpar - 4 parameters.
zlorentz - 3 parameters.
zpowerlw - 2 parameters.
zvlorentz - 3 parameters.
zvoigt - 4 parameters.
zvvoigt - 4 parameters.
zvagauss - 3 parameters.
zvgauss - 3 parameters.
bwcycl - 12 parameters.

Multiplicative models
---------------------
absori - 6 parameters.
acisabs - 8 parameters.
constant - 1 parameter.
cabs - 1 parameter.
cyclabs - 5 parameters.
dust - 2 parameters.
edge - 2 parameters.
expabs - 1 parameter.
expfac - 3 parameters.
gabs - 3 parameters.
heilin - 3 parameters.
highecut - 2 parameters.
hrefl - 8 parameters.
ismabs - 31 parameters.
ismdust - 3 parameters.
logconst - 1 parameter.
log10con - 1 parameter.
lorabs - 3 parameters.
lyman - 4 parameters.
notch - 3 parameters.
olivineabs - 2 parameters.
pcfabs - 2 parameters.
phabs - 1 parameter.
plabs - 2 parameters.
polconst - 2 parameters.
pollin - 4 parameters.
polpow - 4 parameters.
pwab - 3 parameters.
redden - 1 parameter.
smedge - 4 parameters.
spexpcut - 2 parameters.
spline - 6 parameters.
sssice - 1 parameter.
swind1 - 4 parameters.
tbabs - 1 parameter.
tbfeo - 4 parameters.
tbgas - 2 parameters.
tbgrain - 6 parameters.
tbvarabs - 42 parameters.
tbpcf - 3 parameters.
tbrel - 42 parameters.
uvred - 1 parameter.
varabs - 18 parameters.
vgabs - 3 parameters.
vlorabs - 3 parameters.
voigtabs - 4 parameters.
vphabs - 18 parameters.
vvoigtabs - 4 parameters.
wabs - 1 parameter.
wndabs - 2 parameters.
xion - 13 parameters.
xscat - 4 parameters.
zbabs - 4 parameters.
zdust - 4 parameters.
zedge - 3 parameters.
zgabs - 4 parameters.
zhighect - 3 parameters.
zigm - 3 parameters.
zlorabs - 4 parameters.
zpcfabs - 3 parameters.
zphabs - 2 parameters.
zvlorabs - 4 parameters.
zvoigtabs - 5 parameters.
zvvoigtabs - 5 parameters.
zxipab - 5 parameters.
zxipcf - 4 parameters.
zredden - 2 parameters.
zsmdust - 4 parameters.
ztbabs - 2 parameters.
zvarabs - 19 parameters.
zvfeabs - 5 parameters.
zvgabs - 4 parameters.
zvphabs - 19 parameters.
zwabs - 2 parameters.
zwndabs - 3 parameters.

Convolution models
------------------
kyconv - 12 parameters.
rgsext - 2 parameters.
rgsxsrc - 1 parameter.
cflux - 3 parameters.
clumin - 4 parameters.
cglumin - 4 parameters.
cpflux - 3 parameters.
gsmooth - 2 parameters.
ireflect - 7 parameters.
kdblur - 4 parameters.
kdblur2 - 6 parameters.
kerrconv - 7 parameters.
lsmooth - 2 parameters.
partcov - 1 parameter.
rdblur - 4 parameters.
reflect - 5 parameters.
rfxconv - 5 parameters.
simpl - 3 parameters.
thcomp - 4 parameters.
vashift - 1 parameter.
vmshift - 1 parameter.
xilconv - 6 parameters.
zashift - 1 parameter.
zmshift - 1 parameter.

)doc";
    m.def("_init", &xspex::init, "Initializes data directory locations needed by the models.");
    m.def("version", &xspex::get_version, "The version of the Xspec model library.");
    m.def("chatter", &xspex::get_chatter, "Get the Xspec chatter level.");
    m.def("chatter", &xspex::set_chatter, "Set the Xspec chatter level.", "lvl"_a);
    m.def("abundance", &xspex::get_abundance, "Get the abundance-table setting.");
    m.def("abundance", &xspex::set_abundance, "Set the abundance-table setting.", "table"_a);
    m.def("element_abundance", &xspex::abundance_by_name, "Get the abundance setting for an element given the name.", "name"_a);
    m.def("element_abundance", &xspex::abundance_by_z, "Get the abundance setting for an element given the atomic number.", "z"_a);
    m.def("element_name", &xspex::element_name_by_z, "Get the name of an element given the atomic number.", "z"_a);
    m.attr("number_elements") = xspex::number_elements;
    m.def("cross_section", &xspex::get_cross_section, "Get the cross-section-table setting.");
    m.def("cross_section", &xspex::set_cross_section, "Set the cross-section-table setting.", "table"_a);
    m.def("cosmology", &xspex::get_cosmology, "Get the current cosmology (H0, q0, lambda0).");
    m.def("cosmology", &xspex::set_cosmology, "Set the current cosmology (H0, q0, lambda0).", "H0"_a, "q0"_a, "lambda0"_a);

    // XFLT keyword handling: the names are hardly instructive. We could
    // just have an overloaded XFLT method which either queries or sets
    // the values, and then leave the rest to the user to do in Python.
    //
    m.def(
        "clear_xflt",
	    []() { return FunctionUtility::clearXFLT(); },
	    "Clear the XFLT database for all spectra."
    );

    m.def(
        "get_number_xflt",
	    [](int ifl) { return FunctionUtility::getNumberXFLT(ifl); },
	    "How many XFLT keywords are defined for the spectrum?",
	    "spectrum"_a=1
    );

    m.def(
        "get_xflt",
	    [](int ifl) { return FunctionUtility::getAllXFLT(ifl); },
	    "What are all the XFLT keywords for the spectrum?",
	    "spectrum"_a=1,
	    py::return_value_policy::reference
    );

    m.def(
        "get_xflt",
	    [](int ifl, int i) { return FunctionUtility::getXFLT(ifl, i); },
	    "Return the given XFLT key.",
	    "spectrum"_a, "key"_a
    );

    m.def(
        "get_xflt",
	    [](int ifl, string skey) { return FunctionUtility::getXFLT(ifl, skey); },
	    "Return the given XFLT name.",
	    "spectrum"_a, "name"_a
    );

    m.def(
        "in_xflt",
	    [](int ifl, int i) { return FunctionUtility::inXFLT(ifl, i); },
	    "Is the given XFLT key set?",
	    "spectrum"_a, "key"_a
    );

    m.def(
        "in_xflt",
	    [](int ifl, string skey) { return FunctionUtility::inXFLT(ifl, skey); },
	    "Is the given XFLT name set?.",
	    "spectrum"_a, "name"_a
    );

    m.def(
        "set_xflt",
	    [](int ifl, const std::map<string, Real>& values) { FunctionUtility::loadXFLT(ifl, values); },
	    "Set the XFLT keywords for a spectrum",
	    "spectrum"_a, "values"_a
    );

    // Model database - as with XFLT how much do we just leave to Python?
    //
    // What are the memory requirements?
    //
    m.def(
        "clear_model_string",
	    []() { return FunctionUtility::eraseModelStringDataBase(); },
	    "Clear the model string database."
    );

    m.def(
        "get_model_string",
	    []() { return FunctionUtility::modelStringDataBase(); },
	    "Get the model string database.",
	    py::return_value_policy::reference
    );

    m.def(
        "get_model_string",
	    [](const string& key) {
	        auto answer = FunctionUtility::getModelString(key);
	        if (answer == FunctionUtility::NOT_A_KEY()) throw pybind11::key_error(key);
	        return answer;
	    },
	    "Get the key from the model string database.",
	    "key"_a
	);

    m.def(
        "set_model_string",
	    [](const string& key, const string& value) { FunctionUtility::setModelString(key, value); },
	    "Get the key from the model string database.",
	    "key"_a, "value"_a
    );

    // "keyword" database values - similar to XFLT we could leave most of this to
    // Python.
    //
    m.def(
        "clear_db",
	    []() { return FunctionUtility::clearDb(); },
	    "Clear the keyword database."
    );

    m.def(
        "get_db",
	    []() { return FunctionUtility::getAllDbValues(); },
	    "Get the keyword database.",
	    py::return_value_policy::reference
    );

    // If the keyword is not an element then we get a string message and a set
    // return value. Catching this is annoying.
    //
    m.def(
        "get_db",
	    [](const string keyword) {
	        std::ostringstream local;
	        auto cerr_buff = std::cerr.rdbuf();
	        std::cerr.rdbuf(local.rdbuf());

	        // Assume this can not throw an error
	        auto answer = FunctionUtility::getDbValue(keyword);

	        std::cerr.rdbuf(cerr_buff);
	        if (answer == BADVAL) throw pybind11::key_error(keyword);

	        return answer;
	    },
	    "Get the keyword value from the database.",
	    "keyword"_a
    );

    m.def(
        "set_db",
	    [](const string keyword, const double value) {
	        FunctionUtility::loadDbValue(keyword, value);
	    },
	    "Set the keyword in the database to the given value.",
	    "keyword"_a, "value"_a
    );

    m.def("table_model", &xspex::wrapper_table_model<float>, "Call Xspec table model.", "table"_a, "table_type"_a, "pars"_a, "energies"_a, "spectrum"_a=1);

    m.def("xla_registrations", &xla_registrations, "Registrations of XLA ops.");

    // Add the models, auto-generated from the model.dat file.
    m.def("agauss", xspex::wrapper_C<double, C_agauss, 2>, "The Xspec additive agauss model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("agnsed", xspex::wrapper_f<float, agnsed_, 15>, "The Xspec additive agnsed model with 15 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("agnslim", xspex::wrapper_f<float, agnslim_, 14>, "The Xspec additive agnslim model with 14 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("apec", xspex::wrapper_C<double, C_apec, 3>, "The Xspec additive apec model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bapec", xspex::wrapper_C<double, C_bapec, 4>, "The Xspec additive bapec model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bcempow", xspex::wrapper_C<double, C_bcempow, 7>, "The Xspec additive bcempow model with 7 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bcheb6", xspex::wrapper_C<double, C_bcheb6, 11>, "The Xspec additive bcheb6 model with 11 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bcie", xspex::wrapper_C<double, C_bcie, 5>, "The Xspec additive bcie model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bcoolflow", xspex::wrapper_C<double, C_bcoolflow, 6>, "The Xspec additive bcoolflow model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bcph", xspex::wrapper_C<double, C_bcph, 5>, "The Xspec additive bcph model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bequil", xspex::wrapper_C<double, C_bequil, 4>, "The Xspec additive bequil model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bexpcheb6", xspex::wrapper_C<double, C_bexpcheb6, 11>, "The Xspec additive bexpcheb6 model with 11 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bgadem", xspex::wrapper_C<double, C_bgaussDem, 7>, "The Xspec additive bgadem model with 7 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bgnei", xspex::wrapper_C<double, C_bgnei, 6>, "The Xspec additive bgnei model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bnei", xspex::wrapper_C<double, C_bnei, 5>, "The Xspec additive bnei model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bsnapec", xspex::wrapper_C<double, C_bsnapec, 7>, "The Xspec additive bsnapec model with 7 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("btapec", xspex::wrapper_C<double, C_btapec, 5>, "The Xspec additive btapec model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bbody", xspex::wrapper_f<float, xsblbd_, 1>, "The Xspec additive bbody model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("bbodyrad", xspex::wrapper_f<float, xsbbrd_, 1>, "The Xspec additive bbodyrad model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("bexrav", xspex::wrapper_C<double, C_xsbexrav, 9>, "The Xspec additive bexrav model with 9 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bexriv", xspex::wrapper_C<double, C_xsbexriv, 11>, "The Xspec additive bexriv model with 11 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bknpower", xspex::wrapper_C<double, C_brokenPowerLaw, 3>, "The Xspec additive bknpower model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bkn2pow", xspex::wrapper_C<double, C_broken2PowerLaw, 5>, "The Xspec additive bkn2pow model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bmc", xspex::wrapper_f<float, xsbmc_, 3>, "The Xspec additive bmc model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("bnpshock", xspex::wrapper_C<double, C_bnpshock, 7>, "The Xspec additive bnpshock model with 7 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bpshock", xspex::wrapper_C<double, C_bpshock, 6>, "The Xspec additive bpshock model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bremss", xspex::wrapper_f<float, xsbrms_, 1>, "The Xspec additive bremss model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("brnei", xspex::wrapper_C<double, C_brnei, 6>, "The Xspec additive brnei model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bsedov", xspex::wrapper_C<double, C_bsedov, 6>, "The Xspec additive bsedov model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvapec", xspex::wrapper_C<double, C_bvapec, 16>, "The Xspec additive bvapec model with 16 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvcempow", xspex::wrapper_C<double, C_bvcempow, 20>, "The Xspec additive bvcempow model with 20 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvcheb6", xspex::wrapper_C<double, C_bvcheb6, 24>, "The Xspec additive bvcheb6 model with 24 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvcie", xspex::wrapper_C<double, C_bvcie, 17>, "The Xspec additive bvcie model with 17 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvcoolflow", xspex::wrapper_C<double, C_bvcoolflow, 19>, "The Xspec additive bvcoolflow model with 19 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvcph", xspex::wrapper_C<double, C_bvcph, 18>, "The Xspec additive bvcph model with 18 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvequil", xspex::wrapper_C<double, C_bvequil, 15>, "The Xspec additive bvequil model with 15 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvexpcheb6", xspex::wrapper_C<double, C_bvexpcheb6, 24>, "The Xspec additive bvexpcheb6 model with 24 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvgadem", xspex::wrapper_C<double, C_bvgaussDem, 20>, "The Xspec additive bvgadem model with 20 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvgnei", xspex::wrapper_C<double, C_bvgnei, 18>, "The Xspec additive bvgnei model with 18 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvnei", xspex::wrapper_C<double, C_bvnei, 17>, "The Xspec additive bvnei model with 17 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvnpshock", xspex::wrapper_C<double, C_bvnpshock, 19>, "The Xspec additive bvnpshock model with 19 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvpshock", xspex::wrapper_C<double, C_bvpshock, 18>, "The Xspec additive bvpshock model with 18 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvrnei", xspex::wrapper_C<double, C_bvrnei, 18>, "The Xspec additive bvrnei model with 18 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvsedov", xspex::wrapper_C<double, C_bvsedov, 18>, "The Xspec additive bvsedov model with 18 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvtapec", xspex::wrapper_C<double, C_bvtapec, 17>, "The Xspec additive bvtapec model with 17 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvvapec", xspex::wrapper_C<double, C_bvvapec, 33>, "The Xspec additive bvvapec model with 33 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvvcie", xspex::wrapper_C<double, C_bvvcie, 34>, "The Xspec additive bvvcie model with 34 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvvgadem", xspex::wrapper_C<double, C_bvvgaussDem, 36>, "The Xspec additive bvvgadem model with 36 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvvgnei", xspex::wrapper_C<double, C_bvvgnei, 35>, "The Xspec additive bvvgnei model with 35 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvvnei", xspex::wrapper_C<double, C_bvvnei, 34>, "The Xspec additive bvvnei model with 34 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvvnpshock", xspex::wrapper_C<double, C_bvvnpshock, 36>, "The Xspec additive bvvnpshock model with 36 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvvpshock", xspex::wrapper_C<double, C_bvvpshock, 35>, "The Xspec additive bvvpshock model with 35 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvvrnei", xspex::wrapper_C<double, C_bvvrnei, 35>, "The Xspec additive bvvrnei model with 35 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvvsedov", xspex::wrapper_C<double, C_bvvsedov, 35>, "The Xspec additive bvvsedov model with 35 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvvtapec", xspex::wrapper_C<double, C_bvvtapec, 34>, "The Xspec additive bvvtapec model with 34 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvvwdem", xspex::wrapper_C<double, C_bvvwDem, 37>, "The Xspec additive bvvwdem model with 37 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bvwdem", xspex::wrapper_C<double, C_bvwDem, 21>, "The Xspec additive bvwdem model with 21 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bwdem", xspex::wrapper_C<double, C_bwDem, 8>, "The Xspec additive bwdem model with 8 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("c6mekl", xspex::wrapper_C<double, C_c6mekl, 10>, "The Xspec additive c6mekl model with 10 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("c6pmekl", xspex::wrapper_C<double, C_c6pmekl, 10>, "The Xspec additive c6pmekl model with 10 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("c6pvmkl", xspex::wrapper_C<double, C_c6pvmkl, 23>, "The Xspec additive c6pvmkl model with 23 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("c6vmekl", xspex::wrapper_C<double, C_c6vmekl, 23>, "The Xspec additive c6vmekl model with 23 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("carbatm", xspex::wrapper_C<double, C_carbatm, 3>, "The Xspec additive carbatm model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("cemekl", xspex::wrapper_C<double, C_cemMekal, 6>, "The Xspec additive cemekl model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("cempow", xspex::wrapper_C<double, C_cempow, 6>, "The Xspec additive cempow model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("cevmkl", xspex::wrapper_C<double, C_cemVMekal, 19>, "The Xspec additive cevmkl model with 19 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("cflow", xspex::wrapper_C<double, C_xscflw, 5>, "The Xspec additive cflow model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("cheb6", xspex::wrapper_C<double, C_cheb6, 10>, "The Xspec additive cheb6 model with 10 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("cie", xspex::wrapper_C<double, C_cie, 4>, "The Xspec additive cie model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("compbb", xspex::wrapper_f<float, compbb_, 3>, "The Xspec additive compbb model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("compmag", xspex::wrapper_C<double, xscompmag, 8>, "The Xspec additive compmag model with 8 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("compls", xspex::wrapper_f<float, compls_, 2>, "The Xspec additive compls model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("compps", xspex::wrapper_C<double, C_xscompps, 19>, "The Xspec additive compps model with 19 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("compst", xspex::wrapper_f<float, compst_, 2>, "The Xspec additive compst model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("comptb", xspex::wrapper_C<double, xscomptb, 6>, "The Xspec additive comptb model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("compth", xspex::wrapper_C<double, C_xscompth, 20>, "The Xspec additive compth model with 20 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("comptt", xspex::wrapper_f<float, xstitg_, 5>, "The Xspec additive comptt model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("coolflow", xspex::wrapper_C<double, C_coolflow, 5>, "The Xspec additive coolflow model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("cph", xspex::wrapper_C<double, C_cph, 4>, "The Xspec additive cph model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("cplinear", xspex::wrapper_C<double, C_cplinear, 20>, "The Xspec additive cplinear model with 20 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("cutoffpl", xspex::wrapper_C<double, C_cutoffPowerLaw, 2>, "The Xspec additive cutoffpl model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("disk", xspex::wrapper_f<float, disk_, 3>, "The Xspec additive disk model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("diskir", xspex::wrapper_f<float, diskir_, 8>, "The Xspec additive diskir model with 8 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("diskbb", xspex::wrapper_f<float, xsdskb_, 1>, "The Xspec additive diskbb model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("diskline", xspex::wrapper_C<double, C_diskline, 5>, "The Xspec additive diskline model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("diskm", xspex::wrapper_f<float, diskm_, 4>, "The Xspec additive diskm model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("disko", xspex::wrapper_f<float, disko_, 4>, "The Xspec additive disko model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("diskpbb", xspex::wrapper_f<float, diskpbb_, 2>, "The Xspec additive diskpbb model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("diskpn", xspex::wrapper_f<float, xsdiskpn_, 2>, "The Xspec additive diskpn model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("eebremss", xspex::wrapper_C<double, C_eebremss, 3>, "The Xspec additive eebremss model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("eplogpar", xspex::wrapper_f<float, eplogpar_, 2>, "The Xspec additive eplogpar model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("eqpair", xspex::wrapper_C<double, C_xseqpair, 20>, "The Xspec additive eqpair model with 20 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("eqtherm", xspex::wrapper_C<double, C_xseqth, 20>, "The Xspec additive eqtherm model with 20 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("equil", xspex::wrapper_C<double, C_equil, 3>, "The Xspec additive equil model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("expdec", xspex::wrapper_f<float, xsxpdec_, 1>, "The Xspec additive expdec model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("expcheb6", xspex::wrapper_C<double, C_expcheb6, 10>, "The Xspec additive expcheb6 model with 10 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("ezdiskbb", xspex::wrapper_f<float, ezdiskbb_, 1>, "The Xspec additive ezdiskbb model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("feklor", xspex::wrapper_C<double, C_FeKfromSevenLorentzians, 0>, "The Xspec additive feklor model with no parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("gauss", xspex::wrapper_C<double, C_gaussianLine, 2>, "The Xspec additive gauss model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("gadem", xspex::wrapper_C<double, C_gaussDem, 6>, "The Xspec additive gadem model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("gnei", xspex::wrapper_C<double, C_gnei, 5>, "The Xspec additive gnei model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("grad", xspex::wrapper_f<float, grad_, 6>, "The Xspec additive grad model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("grbcomp", xspex::wrapper_C<double, xsgrbcomp, 9>, "The Xspec additive grbcomp model with 9 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("grbjet", xspex::wrapper_C<double, xsgrbjet, 13>, "The Xspec additive grbjet model with 13 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("grbm", xspex::wrapper_f<float, xsgrbm_, 3>, "The Xspec additive grbm model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("hatm", xspex::wrapper_C<double, C_hatm, 3>, "The Xspec additive hatm model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("jet", xspex::wrapper_f<float, jet_, 15>, "The Xspec additive jet model with 15 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("kerrbb", xspex::wrapper_C<double, C_kerrbb, 9>, "The Xspec additive kerrbb model with 9 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("kerrd", xspex::wrapper_C<double, C_kerrd, 7>, "The Xspec additive kerrd model with 7 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("kerrdisk", xspex::wrapper_C<double, C_spin, 9>, "The Xspec additive kerrdisk model with 9 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("kyconv", xspex::wrapper_con_f<float, kyconv_, 12>, "The Xspec convolution kyconv model with 12 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1);
    m.def("kyrline", xspex::wrapper_f<float, kyrline_, 11>, "The Xspec additive kyrline model with 11 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("laor", xspex::wrapper_C<double, C_laor, 5>, "The Xspec additive laor model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("laor2", xspex::wrapper_C<double, C_laor2, 7>, "The Xspec additive laor2 model with 7 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("logpar", xspex::wrapper_C<double, C_logpar, 3>, "The Xspec additive logpar model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("lorentz", xspex::wrapper_C<double, C_lorentzianLine, 2>, "The Xspec additive lorentz model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("meka", xspex::wrapper_C<double, C_meka, 4>, "The Xspec additive meka model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("mekal", xspex::wrapper_C<double, C_mekal, 5>, "The Xspec additive mekal model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("mkcflow", xspex::wrapper_C<double, C_xsmkcf, 5>, "The Xspec additive mkcflow model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("nei", xspex::wrapper_C<double, C_nei, 4>, "The Xspec additive nei model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("nlapec", xspex::wrapper_C<double, C_nlapec, 3>, "The Xspec additive nlapec model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("npshock", xspex::wrapper_C<double, C_npshock, 6>, "The Xspec additive npshock model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("nsa", xspex::wrapper_f<float, nsa_, 4>, "The Xspec additive nsa model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("nsagrav", xspex::wrapper_f<float, nsagrav_, 3>, "The Xspec additive nsagrav model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("nsatmos", xspex::wrapper_f<float, nsatmos_, 4>, "The Xspec additive nsatmos model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("nsmax", xspex::wrapper_C<double, C_nsmax, 3>, "The Xspec additive nsmax model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("nsmaxg", xspex::wrapper_C<double, C_nsmaxg, 5>, "The Xspec additive nsmaxg model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("nsx", xspex::wrapper_C<double, C_nsx, 5>, "The Xspec additive nsx model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("nteea", xspex::wrapper_C<double, C_xsnteea, 15>, "The Xspec additive nteea model with 15 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("nthcomp", xspex::wrapper_C<double, C_nthcomp, 5>, "The Xspec additive nthcomp model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("optxagn", xspex::wrapper_f<float, optxagn_, 13>, "The Xspec additive optxagn model with 13 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("optxagnf", xspex::wrapper_f<float, optxagnf_, 11>, "The Xspec additive optxagnf model with 11 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("pegpwrlw", xspex::wrapper_f<float, xspegp_, 3>, "The Xspec additive pegpwrlw model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("pexmon", xspex::wrapper_f<float, pexmon_, 7>, "The Xspec additive pexmon model with 7 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("pexrav", xspex::wrapper_C<double, C_xspexrav, 7>, "The Xspec additive pexrav model with 7 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("pexriv", xspex::wrapper_C<double, C_xspexriv, 9>, "The Xspec additive pexriv model with 9 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("plcabs", xspex::wrapper_f<float, xsp1tr_, 10>, "The Xspec additive plcabs model with 10 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("powerlaw", xspex::wrapper_C<double, C_powerLaw, 1>, "The Xspec additive powerlaw model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("posm", xspex::wrapper_f<float, xsposm_, 0>, "The Xspec additive posm model with no parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("pshock", xspex::wrapper_C<double, C_pshock, 5>, "The Xspec additive pshock model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("qsosed", xspex::wrapper_f<float, qsosed_, 6>, "The Xspec additive qsosed model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("raymond", xspex::wrapper_C<double, C_raysmith, 3>, "The Xspec additive raymond model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("redge", xspex::wrapper_f<float, xredge_, 2>, "The Xspec additive redge model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("refsch", xspex::wrapper_f<float, xsrefsch_, 13>, "The Xspec additive refsch model with 13 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("rgsext", xspex::wrapper_con_C<double, C_rgsExtendedSource, 2>, "The Xspec convolution rgsext model with 2 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("rgsxsrc", xspex::wrapper_con_C<double, C_rgsxsrc, 1>, "The Xspec convolution rgsxsrc model with 1 parameter.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("rnei", xspex::wrapper_C<double, C_rnei, 5>, "The Xspec additive rnei model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("sedov", xspex::wrapper_C<double, C_sedov, 5>, "The Xspec additive sedov model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("sirf", xspex::wrapper_C<double, C_sirf, 9>, "The Xspec additive sirf model with 9 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("slimbh", xspex::wrapper_C<double, slimbbmodel, 9>, "The Xspec additive slimbh model with 9 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("smaug", xspex::wrapper_C<double, xsmaug, 22>, "The Xspec additive smaug model with 22 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("snapec", xspex::wrapper_C<double, C_snapec, 6>, "The Xspec additive snapec model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("srcut", xspex::wrapper_f<float, srcut_, 2>, "The Xspec additive srcut model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("sresc", xspex::wrapper_f<float, sresc_, 2>, "The Xspec additive sresc model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("ssa", xspex::wrapper_f<float, ssa_, 2>, "The Xspec additive ssa model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("sssed", xspex::wrapper_f<float, sssed_, 14>, "The Xspec additive sssed model with 14 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("step", xspex::wrapper_f<float, xsstep_, 2>, "The Xspec additive step model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("tapec", xspex::wrapper_C<double, C_tapec, 4>, "The Xspec additive tapec model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vagauss", xspex::wrapper_C<double, C_vagauss, 2>, "The Xspec additive vagauss model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vapec", xspex::wrapper_C<double, C_vapec, 15>, "The Xspec additive vapec model with 15 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vbremss", xspex::wrapper_f<float, xsbrmv_, 2>, "The Xspec additive vbremss model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("vcempow", xspex::wrapper_C<double, C_vcempow, 19>, "The Xspec additive vcempow model with 19 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vcheb6", xspex::wrapper_C<double, C_vcheb6, 23>, "The Xspec additive vcheb6 model with 23 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vcie", xspex::wrapper_C<double, C_vcie, 16>, "The Xspec additive vcie model with 16 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vcoolflow", xspex::wrapper_C<double, C_vcoolflow, 18>, "The Xspec additive vcoolflow model with 18 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vcph", xspex::wrapper_C<double, C_vcph, 17>, "The Xspec additive vcph model with 17 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vexpcheb6", xspex::wrapper_C<double, C_vexpcheb6, 23>, "The Xspec additive vexpcheb6 model with 23 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vequil", xspex::wrapper_C<double, C_vequil, 14>, "The Xspec additive vequil model with 14 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vgadem", xspex::wrapper_C<double, C_vgaussDem, 19>, "The Xspec additive vgadem model with 19 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vgauss", xspex::wrapper_C<double, C_vgaussianLine, 2>, "The Xspec additive vgauss model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vgnei", xspex::wrapper_C<double, C_vgnei, 17>, "The Xspec additive vgnei model with 17 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vlorentz", xspex::wrapper_C<double, C_vlorentzianLine, 2>, "The Xspec additive vlorentz model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vmeka", xspex::wrapper_C<double, C_vmeka, 17>, "The Xspec additive vmeka model with 17 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vmekal", xspex::wrapper_C<double, C_vmekal, 18>, "The Xspec additive vmekal model with 18 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vmcflow", xspex::wrapper_C<double, C_xsvmcf, 18>, "The Xspec additive vmcflow model with 18 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vnei", xspex::wrapper_C<double, C_vnei, 16>, "The Xspec additive vnei model with 16 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vnpshock", xspex::wrapper_C<double, C_vnpshock, 18>, "The Xspec additive vnpshock model with 18 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("voigt", xspex::wrapper_C<double, C_voigtLine, 3>, "The Xspec additive voigt model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vpshock", xspex::wrapper_C<double, C_vpshock, 17>, "The Xspec additive vpshock model with 17 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vraymond", xspex::wrapper_C<double, C_vraysmith, 14>, "The Xspec additive vraymond model with 14 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vrnei", xspex::wrapper_C<double, C_vrnei, 17>, "The Xspec additive vrnei model with 17 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vsedov", xspex::wrapper_C<double, C_vsedov, 17>, "The Xspec additive vsedov model with 17 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vtapec", xspex::wrapper_C<double, C_vtapec, 16>, "The Xspec additive vtapec model with 16 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvapec", xspex::wrapper_C<double, C_vvapec, 32>, "The Xspec additive vvapec model with 32 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvcie", xspex::wrapper_C<double, C_vvcie, 33>, "The Xspec additive vvcie model with 33 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvgadem", xspex::wrapper_C<double, C_vvgaussDem, 35>, "The Xspec additive vvgadem model with 35 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvgnei", xspex::wrapper_C<double, C_vvgnei, 34>, "The Xspec additive vvgnei model with 34 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvnei", xspex::wrapper_C<double, C_vvnei, 33>, "The Xspec additive vvnei model with 33 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvnpshock", xspex::wrapper_C<double, C_vvnpshock, 35>, "The Xspec additive vvnpshock model with 35 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvoigt", xspex::wrapper_C<double, C_vvoigtLine, 3>, "The Xspec additive vvoigt model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvpshock", xspex::wrapper_C<double, C_vvpshock, 34>, "The Xspec additive vvpshock model with 34 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvrnei", xspex::wrapper_C<double, C_vvrnei, 34>, "The Xspec additive vvrnei model with 34 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvsedov", xspex::wrapper_C<double, C_vvsedov, 34>, "The Xspec additive vvsedov model with 34 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvtapec", xspex::wrapper_C<double, C_vvtapec, 33>, "The Xspec additive vvtapec model with 33 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vvwdem", xspex::wrapper_C<double, C_vvwDem, 36>, "The Xspec additive vvwdem model with 36 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vwdem", xspex::wrapper_C<double, C_vwDem, 20>, "The Xspec additive vwdem model with 20 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("wdem", xspex::wrapper_C<double, C_wDem, 7>, "The Xspec additive wdem model with 7 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zagauss", xspex::wrapper_C<double, C_zagauss, 3>, "The Xspec additive zagauss model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zbbody", xspex::wrapper_f<float, xszbod_, 2>, "The Xspec additive zbbody model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zbknpower", xspex::wrapper_C<double, C_zBrokenPowerLaw, 4>, "The Xspec additive zbknpower model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zbremss", xspex::wrapper_f<float, xszbrm_, 2>, "The Xspec additive zbremss model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zcutoffpl", xspex::wrapper_C<double, C_zcutoffPowerLaw, 3>, "The Xspec additive zcutoffpl model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zfeklor", xspex::wrapper_C<double, C_zFeKfromSevenLorentzians, 1>, "The Xspec additive zfeklor model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zgauss", xspex::wrapper_C<double, C_xszgau, 3>, "The Xspec additive zgauss model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zkerrbb", xspex::wrapper_C<double, C_zkerrbb, 9>, "The Xspec additive zkerrbb model with 9 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zlogpar", xspex::wrapper_C<double, C_zLogpar, 4>, "The Xspec additive zlogpar model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zlorentz", xspex::wrapper_C<double, C_zlorentzianLine, 3>, "The Xspec additive zlorentz model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zpowerlw", xspex::wrapper_C<double, C_zpowerLaw, 2>, "The Xspec additive zpowerlw model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zvlorentz", xspex::wrapper_C<double, C_zvlorentzianLine, 3>, "The Xspec additive zvlorentz model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zvoigt", xspex::wrapper_C<double, C_zvoigtLine, 4>, "The Xspec additive zvoigt model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zvvoigt", xspex::wrapper_C<double, C_zvvoigtLine, 4>, "The Xspec additive zvvoigt model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("absori", xspex::wrapper_C<double, C_xsabsori, 6>, "The Xspec multiplicative absori model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("acisabs", xspex::wrapper_C<double, C_acisabs, 8>, "The Xspec multiplicative acisabs model with 8 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("constant", xspex::wrapper_f<float, xscnst_, 1>, "The Xspec multiplicative constant model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("cabs", xspex::wrapper_f<float, xscabs_, 1>, "The Xspec multiplicative cabs model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("cyclabs", xspex::wrapper_f<float, xscycl_, 5>, "The Xspec multiplicative cyclabs model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("dust", xspex::wrapper_f<float, xsdust_, 2>, "The Xspec multiplicative dust model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("edge", xspex::wrapper_f<float, xsedge_, 2>, "The Xspec multiplicative edge model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("expabs", xspex::wrapper_f<float, xsabsc_, 1>, "The Xspec multiplicative expabs model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("expfac", xspex::wrapper_f<float, xsexp_, 3>, "The Xspec multiplicative expfac model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("gabs", xspex::wrapper_C<double, C_gaussianAbsorptionLine, 3>, "The Xspec multiplicative gabs model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("heilin", xspex::wrapper_f<float, xsphei_, 3>, "The Xspec multiplicative heilin model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("highecut", xspex::wrapper_f<float, xshecu_, 2>, "The Xspec multiplicative highecut model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("hrefl", xspex::wrapper_f<float, xshrfl_, 8>, "The Xspec multiplicative hrefl model with 8 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("ismabs", xspex::wrapper_F<double, ismabs_, 31>, "The Xspec multiplicative ismabs model with 31 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("ismdust", xspex::wrapper_F<double, ismdust_, 3>, "The Xspec multiplicative ismdust model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("logconst", xspex::wrapper_C<double, C_logconst, 1>, "The Xspec multiplicative logconst model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("log10con", xspex::wrapper_C<double, C_log10con, 1>, "The Xspec multiplicative log10con model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("lorabs", xspex::wrapper_C<double, C_lorentzianAbsorptionLine, 3>, "The Xspec multiplicative lorabs model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("lyman", xspex::wrapper_f<float, xslyman_, 4>, "The Xspec multiplicative lyman model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("notch", xspex::wrapper_f<float, xsntch_, 3>, "The Xspec multiplicative notch model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("olivineabs", xspex::wrapper_F<double, olivineabs_, 2>, "The Xspec multiplicative olivineabs model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("pcfabs", xspex::wrapper_f<float, xsabsp_, 2>, "The Xspec multiplicative pcfabs model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("phabs", xspex::wrapper_f<float, xsphab_, 1>, "The Xspec multiplicative phabs model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("plabs", xspex::wrapper_f<float, xsplab_, 2>, "The Xspec multiplicative plabs model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("polconst", xspex::wrapper_C<double, C_polconst, 2>, "The Xspec multiplicative polconst model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("pollin", xspex::wrapper_C<double, C_pollin, 4>, "The Xspec multiplicative pollin model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("polpow", xspex::wrapper_C<double, C_polpow, 4>, "The Xspec multiplicative polpow model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("pwab", xspex::wrapper_C<double, C_xspwab, 3>, "The Xspec multiplicative pwab model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("redden", xspex::wrapper_f<float, xscred_, 1>, "The Xspec multiplicative redden model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("smedge", xspex::wrapper_f<float, xssmdg_, 4>, "The Xspec multiplicative smedge model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("spexpcut", xspex::wrapper_C<double, C_superExpCutoff, 2>, "The Xspec multiplicative spexpcut model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("spline", xspex::wrapper_f<float, xsspln_, 6>, "The Xspec multiplicative spline model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("sssice", xspex::wrapper_f<float, xssssi_, 1>, "The Xspec multiplicative sssice model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("swind1", xspex::wrapper_C<double, C_swind1, 4>, "The Xspec multiplicative swind1 model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("tbabs", xspex::wrapper_C<double, C_tbabs, 1>, "The Xspec multiplicative tbabs model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("tbfeo", xspex::wrapper_C<double, C_tbfeo, 4>, "The Xspec multiplicative tbfeo model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("tbgas", xspex::wrapper_C<double, C_tbgas, 2>, "The Xspec multiplicative tbgas model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("tbgrain", xspex::wrapper_C<double, C_tbgrain, 6>, "The Xspec multiplicative tbgrain model with 6 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("tbvarabs", xspex::wrapper_C<double, C_tbvabs, 42>, "The Xspec multiplicative tbvarabs model with 42 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("tbpcf", xspex::wrapper_C<double, C_tbpcf, 3>, "The Xspec multiplicative tbpcf model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("tbrel", xspex::wrapper_C<double, C_tbrel, 42>, "The Xspec multiplicative tbrel model with 42 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("uvred", xspex::wrapper_f<float, xsred_, 1>, "The Xspec multiplicative uvred model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("varabs", xspex::wrapper_f<float, xsabsv_, 18>, "The Xspec multiplicative varabs model with 18 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("vgabs", xspex::wrapper_C<double, C_vgaussianAbsorptionLine, 3>, "The Xspec multiplicative vgabs model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vlorabs", xspex::wrapper_C<double, C_vlorentzianAbsorptionLine, 3>, "The Xspec multiplicative vlorabs model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("voigtabs", xspex::wrapper_C<double, C_voigtAbsorptionLine, 4>, "The Xspec multiplicative voigtabs model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vphabs", xspex::wrapper_f<float, xsvphb_, 18>, "The Xspec multiplicative vphabs model with 18 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("vvoigtabs", xspex::wrapper_C<double, C_vvoigtAbsorptionLine, 4>, "The Xspec multiplicative vvoigtabs model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("wabs", xspex::wrapper_f<float, xsabsw_, 1>, "The Xspec multiplicative wabs model with 1 parameter.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("wndabs", xspex::wrapper_f<float, xswnab_, 2>, "The Xspec multiplicative wndabs model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("xion", xspex::wrapper_f<float, xsxirf_, 13>, "The Xspec multiplicative xion model with 13 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("xscat", xspex::wrapper_C<double, C_xscatmodel, 4>, "The Xspec multiplicative xscat model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zbabs", xspex::wrapper_C<double, xszbabs, 4>, "The Xspec multiplicative zbabs model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zdust", xspex::wrapper_f<float, mszdst_, 4>, "The Xspec multiplicative zdust model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zedge", xspex::wrapper_f<float, xszedg_, 3>, "The Xspec multiplicative zedge model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zgabs", xspex::wrapper_C<double, C_zgaussianAbsorptionLine, 4>, "The Xspec multiplicative zgabs model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zhighect", xspex::wrapper_f<float, xszhcu_, 3>, "The Xspec multiplicative zhighect model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zigm", xspex::wrapper_f<float, zigm_, 3>, "The Xspec multiplicative zigm model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zlorabs", xspex::wrapper_C<double, C_zlorentzianAbsorptionLine, 4>, "The Xspec multiplicative zlorabs model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zpcfabs", xspex::wrapper_f<float, xszabp_, 3>, "The Xspec multiplicative zpcfabs model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zphabs", xspex::wrapper_f<float, xszphb_, 2>, "The Xspec multiplicative zphabs model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zvlorabs", xspex::wrapper_C<double, C_zvlorentzianAbsorptionLine, 4>, "The Xspec multiplicative zvlorabs model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zvoigtabs", xspex::wrapper_C<double, C_zvoigtAbsorptionLine, 5>, "The Xspec multiplicative zvoigtabs model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zvvoigtabs", xspex::wrapper_C<double, C_zvvoigtAbsorptionLine, 5>, "The Xspec multiplicative zvvoigtabs model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zxipab", xspex::wrapper_f<float, zxipab_, 5>, "The Xspec multiplicative zxipab model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zxipcf", xspex::wrapper_C<double, C_zxipcf, 4>, "The Xspec multiplicative zxipcf model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zredden", xspex::wrapper_f<float, xszcrd_, 2>, "The Xspec multiplicative zredden model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zsmdust", xspex::wrapper_f<float, msldst_, 4>, "The Xspec multiplicative zsmdust model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("ztbabs", xspex::wrapper_C<double, C_ztbabs, 2>, "The Xspec multiplicative ztbabs model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zvagauss", xspex::wrapper_C<double, C_zvagauss, 3>, "The Xspec additive zvagauss model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zvarabs", xspex::wrapper_f<float, xszvab_, 19>, "The Xspec multiplicative zvarabs model with 19 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zvfeabs", xspex::wrapper_f<float, xszvfe_, 5>, "The Xspec multiplicative zvfeabs model with 5 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zvgabs", xspex::wrapper_C<double, C_zvgaussianAbsorptionLine, 4>, "The Xspec multiplicative zvgabs model with 4 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zvgauss", xspex::wrapper_C<double, C_zvgaussianLine, 3>, "The Xspec additive zvgauss model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zvphabs", xspex::wrapper_f<float, xszvph_, 19>, "The Xspec multiplicative zvphabs model with 19 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zwabs", xspex::wrapper_f<float, xszabs_, 2>, "The Xspec multiplicative zwabs model with 2 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("zwndabs", xspex::wrapper_f<float, xszwnb_, 3>, "The Xspec multiplicative zwndabs model with 3 parameters.","pars"_a, "energies"_a, "spectrum"_a=1);
    m.def("cflux", xspex::wrapper_con_C<double, C_cflux, 3>, "The Xspec convolution cflux model with 3 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("clumin", xspex::wrapper_con_C<double, C_clumin, 4>, "The Xspec convolution clumin model with 4 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("cglumin", xspex::wrapper_con_C<double, C_cglumin, 4>, "The Xspec convolution cglumin model with 4 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("cpflux", xspex::wrapper_con_C<double, C_cpflux, 3>, "The Xspec convolution cpflux model with 3 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("gsmooth", xspex::wrapper_con_C<double, C_gsmooth, 2>, "The Xspec convolution gsmooth model with 2 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("ireflect", xspex::wrapper_con_C<double, C_ireflct, 7>, "The Xspec convolution ireflect model with 7 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("kdblur", xspex::wrapper_con_C<double, C_kdblur, 4>, "The Xspec convolution kdblur model with 4 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("kdblur2", xspex::wrapper_con_C<double, C_kdblur2, 6>, "The Xspec convolution kdblur2 model with 6 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("kerrconv", xspex::wrapper_con_C<double, C_spinconv, 7>, "The Xspec convolution kerrconv model with 7 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("lsmooth", xspex::wrapper_con_C<double, C_lsmooth, 2>, "The Xspec convolution lsmooth model with 2 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("partcov", xspex::wrapper_con_C<double, C_PartialCovering, 1>, "The Xspec convolution partcov model with 1 parameter.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("rdblur", xspex::wrapper_con_C<double, C_rdblur, 4>, "The Xspec convolution rdblur model with 4 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("reflect", xspex::wrapper_con_C<double, C_reflct, 5>, "The Xspec convolution reflect model with 5 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("rfxconv", xspex::wrapper_con_C<double, C_rfxconv, 5>, "The Xspec convolution rfxconv model with 5 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("simpl", xspex::wrapper_con_C<double, C_simpl, 3>, "The Xspec convolution simpl model with 3 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("thcomp", xspex::wrapper_con_f<float, thcompf_, 4>, "The Xspec convolution thcomp model with 4 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1);
    m.def("vashift", xspex::wrapper_con_C<double, C_vashift, 1>, "The Xspec convolution vashift model with 1 parameter.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("vmshift", xspex::wrapper_con_C<double, C_vmshift, 1>, "The Xspec convolution vmshift model with 1 parameter.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("xilconv", xspex::wrapper_con_C<double, C_xilconv, 6>, "The Xspec convolution xilconv model with 6 parameters.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zashift", xspex::wrapper_con_C<double, C_zashift, 1>, "The Xspec convolution zashift model with 1 parameter.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("zmshift", xspex::wrapper_con_C<double, C_zmshift, 1>, "The Xspec convolution zmshift model with 1 parameter.","pars"_a, "energies"_a, "model"_a, "spectrum"_a=1, "initStr"_a="");
    m.def("bwcycl", xspex::wrapper_C<double, beckerwolff, 12>, "The Xspec additive bwcycl model with 12 parameters.","pars"_a, "energies"_a, "spectrum"_a=1, "initStr"_a="");
}
