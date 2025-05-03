//===----------------------------------------------------------------------===//
//
//        OpenSees - Open System for Earthquake Engineering Simulation
//
//===----------------------------------------------------------------------===//
//
//
// Description: This file contains the implementation of the
// TclBasicBuilder_addFedeasMaterial() function.
//
// Written: MHS
// Created: Aug 2001
//
#include <tcl.h>
#include <Logging.h>
#include <Parsing.h>
#include <Vector.h>
#include <string.h>

#include <Steel01.h>
#include <Steel02.h>
#include <Concrete01.h>
#include <Concrete02.h>


int
TclBasicBuilder_addUniaxialMetallic(ClientData clientData, Tcl_Interp *interp,
                                  int argc, TCL_Char ** const argv)
{

  BasicModelBuilder *builder = static_cast<BasicModelBuilder *>(clientData);

  if (argc < 3) {
    opserr << "WARNING insufficient number of arguments\n";
    return TCL_ERROR;
  }

  enum Positions {
    E, sigY, Hiso, Hkin, alp, aln, ft, Ets, rat
  };
  int tag;
  if (Tcl_GetInt(interp, argv[2], &tag) != TCL_OK) {
    opserr << "WARNING invalid uniaxialMaterial tag\n";
    return TCL_ERROR;
  }

  UniaxialMaterial *theMaterial = nullptr;

  if (strcmp(argv[1], "Concrete1") == 0 ||
           strcmp(argv[1], "concrete01") == 0) {
    if (argc < 7) {
      opserr << "WARNING invalid number of arguments\n";
      opserr
          << "Want: uniaxialMaterial Concrete01 tag? fpc? epsc0? fpcu? epscu?"
          << endln;
      return TCL_ERROR;
    }

    double fpc, epsc0, fpcu, epscu;

    if (Tcl_GetDouble(interp, argv[3], &fpc) != TCL_OK) {
      opserr << "WARNING invalid fpc\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[4], &epsc0) != TCL_OK) {
      opserr << "WARNING invalid epsc0\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[5], &fpcu) != TCL_OK) {
      opserr << "WARNING invalid fpcu\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[6], &epscu) != TCL_OK) {
      opserr << "WARNING invalid epscu\n";
      return TCL_ERROR;
    }

    theMaterial = new Concrete01(tag, fpc, epsc0, fpcu, epscu);
  }

  else if (strcmp(argv[1], "concr2") == 0) {
    if (argc < 10) {
      opserr << "WARNING invalid number of arguments\n";
      opserr << "Want: uniaxialMaterial Concrete02 tag? fpc? epsc0? fpcu? "
                "epscu? rat? ft? Ets?"
             << endln;
      return TCL_ERROR;
    }

    double fpc, epsc0, fpcu, epscu;
    double rat, ft, Ets;

    if (Tcl_GetDouble(interp, argv[3], &fpc) != TCL_OK) {
      opserr << "WARNING invalid fpc\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[4], &epsc0) != TCL_OK) {
      opserr << "WARNING invalid epsc0\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[5], &fpcu) != TCL_OK) {
      opserr << "WARNING invalid fpcu\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[6], &epscu) != TCL_OK) {
      opserr << "WARNING invalid epscu\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[7], &rat) != TCL_OK) {
      opserr << "WARNING invalid rat\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[8], &ft) != TCL_OK) {
      opserr << "WARNING invalid ft\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[9], &Ets) != TCL_OK) {
      opserr << "WARNING invalid Ets\n";
      return TCL_ERROR;
    }

    theMaterial =
        new Concrete02(tag, fpc, epsc0, fpcu, epscu, rat, ft, Ets);
  }

  else if (strcmp(argv[1], "Steel1") == 0 || 
           strcmp(argv[1], "Steel01") == 0) {
    if (argc < 6) {
      opserr << "WARNING invalid number of arguments\n";
      opserr
          << "Want: uniaxialMaterial Steel01 tag? fy? E? b? <a1? a2? a3? a4?>"
          << endln;
      return TCL_ERROR;
    }

    double fy, E, b;
    double a1, a2, a3, a4;

    if (Tcl_GetDouble(interp, argv[3], &fy) != TCL_OK) {
      opserr << "WARNING invalid fy\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[4], &E) != TCL_OK) {
      opserr << "WARNING invalid E\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[5], &b) != TCL_OK) {
      opserr << "WARNING invalid b\n";
      return TCL_ERROR;
    }
    if (argc > 9) {
      if (Tcl_GetDouble(interp, argv[6], &a1) != TCL_OK) {
        opserr << "WARNING invalid a1\n";
        return TCL_ERROR;
      }
      if (Tcl_GetDouble(interp, argv[7], &a2) != TCL_OK) {
        opserr << "WARNING invalid a2\n";
        return TCL_ERROR;
      }
      if (Tcl_GetDouble(interp, argv[8], &a3) != TCL_OK) {
        opserr << "WARNING invalid a3\n";
        return TCL_ERROR;
      }
      if (Tcl_GetDouble(interp, argv[9], &a4) != TCL_OK) {
        opserr << "WARNING invalid a4\n";
        return TCL_ERROR;
      }
      theMaterial = new Steel01(tag, fy, E, b, a1, a2, a3, a4);
    } else
      theMaterial = new Steel01(tag, fy, E, b);
  }

  else if (strcmp(argv[1], "Steel02") == 0) {
    // uniaxialMaterial Steel02 $tag $Fy $E $b $R0 $cR1 $cR2 <$a1 $a2 $a3 $a4 $sigInit>
    if (argc < 6) {
      opserr << "WARNING invalid number of arguments\n";
      opserr << "Want: uniaxialMaterial Steel02 tag? fy? E? b? <R0? cR1? cR2? "
                "<a1? a2? a3? a4?>>"
             << endln;
      return TCL_ERROR;
    }

    double fy, E, b;
    double R0, cR1, cR2;
    double a1, a2, a3, a4;

    if (Tcl_GetDouble(interp, argv[3], &fy) != TCL_OK) {
      opserr << "WARNING invalid fy\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[4], &E) != TCL_OK) {
      opserr << "WARNING invalid E\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[5], &b) != TCL_OK) {
      opserr << "WARNING invalid b\n";
      return TCL_ERROR;
    }
    if (argc > 8) {
      if (Tcl_GetDouble(interp, argv[6], &R0) != TCL_OK) {
        opserr << "WARNING invalid R0\n";
        return TCL_ERROR;
      }
      if (Tcl_GetDouble(interp, argv[7], &cR1) != TCL_OK) {
        opserr << "WARNING invalid cR1\n";
        return TCL_ERROR;
      }
      if (Tcl_GetDouble(interp, argv[8], &cR2) != TCL_OK) {
        opserr << "WARNING invalid cR2\n";
        return TCL_ERROR;
      }
      if (argc > 12) {
        if (Tcl_GetDouble(interp, argv[9], &a1) != TCL_OK) {
          opserr << "WARNING invalid a1\n";
          return TCL_ERROR;
        }
        if (Tcl_GetDouble(interp, argv[10], &a2) != TCL_OK) {
          opserr << "WARNING invalid a2\n";
          return TCL_ERROR;
        }
        if (Tcl_GetDouble(interp, argv[11], &a3) != TCL_OK) {
          opserr << "WARNING invalid a3\n";
          return TCL_ERROR;
        }
        if (Tcl_GetDouble(interp, argv[12], &a4) != TCL_OK) {
          opserr << "WARNING invalid a4\n";
          return TCL_ERROR;
        }
        theMaterial = new Steel02(tag, fy, E, b, R0, cR1, cR2, a1,
                                               a2, a3, a4);
      } else
        theMaterial = new Steel02(tag, fy, E, b, R0, cR1, cR2);

    } else
      theMaterial = new Steel02(tag, fy, E, b);

  }

  return builder->addTaggedObject<UniaxialMaterial>(*theMaterial);
}

#if 0
#include <FedeasHardeningMaterial.h>
#include <FedeasBond1Material.h>
#include <FedeasBond2Material.h>
#include <FedeasConcr3Material.h>
#include <FedeasHyster1Material.h>
#include <FedeasHyster2Material.h>
#include <PlasticDamageMaterial.h>
int
Cmd(ClientData clientData, Tcl_Interp *interp,
    int argc, TCL_Char ** const argv)
  {
  if (strcmp(argv[1], "Hardening1") == 0 ||
  strcmp(argv[1], "Hardening01") == 0) {
  if (argc < 7) {
  opserr << "WARNING invalid number of arguments\n";
  opserr << "Want: uniaxialMaterial Hardening01 tag? E? sigY? Hiso? Hkin?"
        << endln;
  return TCL_ERROR;
  }

  double E, sigY, Hiso, Hkin;

  if (Tcl_GetDouble(interp, argv[3], &E) != TCL_OK) {
  opserr << "WARNING invalid E\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[4], &sigY) != TCL_OK) {
  opserr << "WARNING invalid sigY\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[5], &Hiso) != TCL_OK) {
  opserr << "WARNING invalid Hiso\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[6], &Hkin) != TCL_OK) {
  opserr << "WARNING invalid Hkin\n";
  return TCL_ERROR;
  }

  theMaterial = new FedeasHardeningMaterial(tag, E, sigY, Hiso, Hkin);
  }

  else if (strcmp(argv[1], "Bond1") == 0 || strcmp(argv[1], "Bond01") == 0) {
  if (argc < 15) {
  opserr << "WARNING invalid number of arguments\n";
  opserr << "Want: uniaxialMaterial Bond01 tag? u1p? q1p? u2p? u3p? q3p? "
            "u1n? q1n? u2n? u3n? q3n? s0? bb?"
        << endln;
  return TCL_ERROR;
  }

  double u1p, q1p, u2p, u3p, q3p;
  double u1n, q1n, u2n, u3n, q3n;
  double s0, bb;

  if (Tcl_GetDouble(interp, argv[3], &u1p) != TCL_OK) {
  opserr << "WARNING invalid u1p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[4], &q1p) != TCL_OK) {
  opserr << "WARNING invalid q1p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[5], &u2p) != TCL_OK) {
  opserr << "WARNING invalid u2p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[6], &u3p) != TCL_OK) {
  opserr << "WARNING invalid u3p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[7], &q3p) != TCL_OK) {
  opserr << "WARNING invalid q3p\n";
  return TCL_ERROR;
  }

  if (Tcl_GetDouble(interp, argv[8], &u1n) != TCL_OK) {
  opserr << "WARNING invalid u1n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[9], &q1n) != TCL_OK) {
  opserr << "WARNING invalid q1n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[10], &u2n) != TCL_OK) {
  opserr << "WARNING invalid u2n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[11], &u3n) != TCL_OK) {
  opserr << "WARNING invalid u3n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[12], &q3n) != TCL_OK) {
  opserr << "WARNING invalid q3n\n";
  return TCL_ERROR;
  }

  if (Tcl_GetDouble(interp, argv[13], &s0) != TCL_OK) {
  opserr << "WARNING invalid s0\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[14], &bb) != TCL_OK) {
  opserr << "WARNING invalid bb\n";
  return TCL_ERROR;
  }

  theMaterial = new FedeasBond1Material(tag, u1p, q1p, u2p, u3p, q3p, u1n,
                                      q1n, u2n, u3n, q3n, s0, bb);
  }

  else if (strcmp(argv[1], "Bond2") == 0 || strcmp(argv[1], "Bond02") == 0) {
  if (argc < 17) {

  opserr << "WARNING invalid number of arguments\n";
  opserr << "Want: uniaxialMaterial Bond02 tag? u1p? q1p? u2p? u3p? q3p? "
            "u1n? q1n? u2n? u3n? q3n? s0? bb? alp? aln?"
        << endln;
  return TCL_ERROR;
  }

  double u1p, q1p, u2p, u3p, q3p;
  double u1n, q1n, u2n, u3n, q3n;
  double s0, bb, alp, aln;

  if (Tcl_GetDouble(interp, argv[3], &u1p) != TCL_OK) {
  opserr << "WARNING invalid u1p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[4], &q1p) != TCL_OK) {
  opserr << "WARNING invalid q1p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[5], &u2p) != TCL_OK) {
  opserr << "WARNING invalid u2p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[6], &u3p) != TCL_OK) {
  opserr << "WARNING invalid u3p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[7], &q3p) != TCL_OK) {
  opserr << "WARNING invalid q3p\n";
  return TCL_ERROR;
  }

  if (Tcl_GetDouble(interp, argv[8], &u1n) != TCL_OK) {
  opserr << "WARNING invalid u1n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[9], &q1n) != TCL_OK) {
  opserr << "WARNING invalid q1n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[10], &u2n) != TCL_OK) {
  opserr << "WARNING invalid u2n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[11], &u3n) != TCL_OK) {
  opserr << "WARNING invalid u3n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[12], &q3n) != TCL_OK) {
  opserr << "WARNING invalid q3n\n";
  return TCL_ERROR;
  }

  if (Tcl_GetDouble(interp, argv[13], &s0) != TCL_OK) {
  opserr << "WARNING invalid s0\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[14], &bb) != TCL_OK) {
  opserr << "WARNING invalid bb\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[15], &alp) != TCL_OK) {
  opserr << "WARNING invalid alp\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[16], &aln) != TCL_OK) {
  opserr << "WARNING invalid aln\n";
  return TCL_ERROR;
  }

  theMaterial = new FedeasBond2Material(tag, u1p, q1p, u2p, u3p, q3p, u1n,
                                      q1n, u2n, u3n, q3n, s0, bb, alp, aln);
  }

  else if (strcmp(argv[1], "Concrete3") == 0 ||
  strcmp(argv[1], "Concrete03") == 0) {
  if (argc < 13) {
  opserr << "WARNING invalid number of arguments\n";
  opserr << "Want: uniaxialMaterial Concrete03 tag? fpc? epsc0? fpcu? "
      "epscu? rat? ft? epst0? ft0? beta? epstu?"
    << endln;
  return TCL_ERROR;
  }

  double fpc, epsc0, fpcu, epscu;
  double rat, ft, epst0, ft0, beta, epstu;

  if (Tcl_GetDouble(interp, argv[3], &fpc) != TCL_OK) {
  opserr << "WARNING invalid fpc\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[4], &epsc0) != TCL_OK) {
  opserr << "WARNING invalid epsc0\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[5], &fpcu) != TCL_OK) {
  opserr << "WARNING invalid fpcu\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[6], &epscu) != TCL_OK) {
  opserr << "WARNING invalid epscu\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[7], &rat) != TCL_OK) {
  opserr << "WARNING invalid rat\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[8], &ft) != TCL_OK) {
  opserr << "WARNING invalid ft\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[9], &epst0) != TCL_OK) {
  opserr << "WARNING invalid epst0\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[10], &ft0) != TCL_OK) {
  opserr << "WARNING invalid ft0\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[11], &beta) != TCL_OK) {
  opserr << "WARNING invalid beta\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[12], &epstu) != TCL_OK) {
  opserr << "WARNING invalid epstu\n";
  return TCL_ERROR;
  }

  theMaterial = new FedeasConcr3Material(tag, fpc, epsc0, fpcu, epscu, rat,
                                  ft, epst0, ft0, beta, epstu);
  }

  else if (strcmp(argv[1], "Hysteretic1") == 0 ||
  strcmp(argv[1], "Hysteretic01") == 0) {
  if (argc < 15) {
  opserr << "WARNING invalid number of arguments\n";
  opserr << "Want: uniaxialMaterial Hysteretic01 tag? s1p? e1p? s2p? e2p? "
      "s1n? e1n? s2n? e1n? px? py? d1? d2?"
    << endln;
  return TCL_ERROR;
  }

  double s1p, e1p, s2p, e2p;
  double s1n, e1n, s2n, e2n;
  double px, py, d1, d2;

  if (Tcl_GetDouble(interp, argv[3], &s1p) != TCL_OK) {
  opserr << "WARNING invalid s1p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[4], &e1p) != TCL_OK) {
  opserr << "WARNING invalid e1p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[5], &s2p) != TCL_OK) {
  opserr << "WARNING invalid s2p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[6], &e2p) != TCL_OK) {
  opserr << "WARNING invalid e2p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[7], &s1n) != TCL_OK) {
  opserr << "WARNING invalid s1n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[8], &e1n) != TCL_OK) {
  opserr << "WARNING invalid e1n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[9], &s2n) != TCL_OK) {
  opserr << "WARNING invalid s2n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[10], &e2n) != TCL_OK) {
  opserr << "WARNING invalid e2n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[11], &px) != TCL_OK) {
  opserr << "WARNING invalid px\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[12], &py) != TCL_OK) {
  opserr << "WARNING invalid py\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[13], &d1) != TCL_OK) {
  opserr << "WARNING invalid d1\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[14], &d2) != TCL_OK) {
  opserr << "WARNING invalid d2\n";
  return TCL_ERROR;
  }

  theMaterial = new FedeasHyster1Material(tag, s1p, e1p, s2p, e2p, s1n, e1n,
                                  s2n, e2n, px, py, d1, d2);
  }

  else if (strcmp(argv[1], "Hysteretic2") == 0 ||
  strcmp(argv[1], "Hysteretic02") == 0) {
  if (argc < 19) {
  opserr << "WARNING invalid number of arguments\n";
  opserr << "Want: uniaxialMaterial Hysteretic02 tag? s1p? e1p? s2p? e2p? "
      "s3p? e3p? s1n? e1n? s2n? e1n? s3n? e3n? px? py? d1? d2?"
    << endln;
  return TCL_ERROR;
  }

  double s1p, e1p, s2p, e2p, s3p, e3p;
  double s1n, e1n, s2n, e2n, s3n, e3n;
  double px, py, d1, d2;

  if (Tcl_GetDouble(interp, argv[3], &s1p) != TCL_OK) {
  opserr << "WARNING invalid s1p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[4], &e1p) != TCL_OK) {
  opserr << "WARNING invalid e1p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[5], &s2p) != TCL_OK) {
  opserr << "WARNING invalid s2p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[6], &e2p) != TCL_OK) {
  opserr << "WARNING invalid e2p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[7], &s3p) != TCL_OK) {
  opserr << "WARNING invalid s2p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[8], &e3p) != TCL_OK) {
  opserr << "WARNING invalid e2p\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[9], &s1n) != TCL_OK) {
  opserr << "WARNING invalid s1n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[10], &e1n) != TCL_OK) {
  opserr << "WARNING invalid e1n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[11], &s2n) != TCL_OK) {
  opserr << "WARNING invalid s2n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[12], &e2n) != TCL_OK) {
  opserr << "WARNING invalid e2n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[13], &s3n) != TCL_OK) {
  opserr << "WARNING invalid s2n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[14], &e3n) != TCL_OK) {
  opserr << "WARNING invalid e2n\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[15], &px) != TCL_OK) {
  opserr << "WARNING invalid px\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[16], &py) != TCL_OK) {
  opserr << "WARNING invalid py\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[17], &d1) != TCL_OK) {
  opserr << "WARNING invalid d1\n";
  return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[18], &d2) != TCL_OK) {
  opserr << "WARNING invalid d2\n";
  return TCL_ERROR;
  }

  theMaterial =
  new FedeasHyster2Material(tag, s1p, e1p, s2p, e2p, s3p, e3p, s1n, e1n,
                        s2n, e2n, s3n, e3n, px, py, d1, d2);
  }

  else if (strcmp(argv[1], "ConcretePlasticDamage") == 0 ||
           strcmp(argv[1], "PlasticDamage") == 0) {
    if (argc < 11) {
      opserr << "WARNING invalid number of arguments\n";
      opserr << "Want: uniaxialMaterial ConcretePlasticDamage tag? $Ec $Gf $Gc "
                "$ft $fcy $fc $ktcr $relax"
             << endln;
      return TCL_ERROR;
    }

    double Ec, Ft, Fc, ft_max, fcy, fc, ktcr, relax;

    if (Tcl_GetDouble(interp, argv[3], &Ec) != TCL_OK) {
      opserr << OpenSees::PromptValueError
             << "invalid Ec\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[4], &Ft) != TCL_OK) {
      opserr << OpenSees::PromptValueError
             << "invalid Ft\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[5], &Fc) != TCL_OK) {
      opserr << OpenSees::PromptValueError
             << "invalid Fc\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[6], &ft_max) != TCL_OK) {
      opserr << OpenSees::PromptValueError
             << "invalid ft_max\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[7], &fcy) != TCL_OK) {
      opserr << OpenSees::PromptValueError
             << "invalid fcy\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[8], &fc) != TCL_OK) {
      opserr << OpenSees::PromptValueError
             << "invalid fc\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[9], &ktcr) != TCL_OK) {
      opserr << OpenSees::PromptValueError
             << "invalid Ktcr\n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[10], &relax) != TCL_OK) {
      opserr << OpenSees::PromptValueError
             << "invalid relax\n";
      return TCL_ERROR;
    }

    theMaterial = new PlasticDamageMaterial(tag, Ec, Ft, Fc, ft_max, fcy, fc,
                                            ktcr, relax);
  }
  else {
    opserr << "WARNING invalid uniaxialMaterial type\n";
    return TCL_ERROR;
  }
}
#endif