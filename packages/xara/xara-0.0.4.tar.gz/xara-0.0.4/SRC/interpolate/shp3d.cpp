//===----------------------------------------------------------------------===//
//
//        OpenSees - Open System for Earthquake Engineering Simulation    
//
//===----------------------------------------------------------------------===//
//
// 3D isoparametric 8-node element shape function
//
// 
//    Purpose: Compute 3-d isoparametric 8-node element shape
//             functions and their derivatives w/r x,y,z
//
//    Inputs:
//       xn[3]     - Natural coordinates of point
//       xl[3][8]  - Nodal coordinates for element
//
//    Outputs:
//       xsj        - Jacobian determinant at point
//       shp[4][8]  - Shape functions and derivatives at point
//                    shp[0][i] = dN_i/dx
//                    shp[1][i] = dN_i/dy
//                    shp[2][i] = dN_i/dzc
//                    shp[3][i] =  N_i
//
//===----------------------------------------------------------------------===//
//
// Ed "C++" Love
//
//===----------------------------------------------------------------------===//
//
void
shp3d(const double xn[3],
            double &xsj,
            double shp[4][8],
            const double xl[3][8])
{

  // Compute shape functions and their natural coord. derivatives

  double ap1 = 1.0 + xn[0];
  double am1 = 1.0 - xn[0];
  double ap2 = 1.0 + xn[1];
  double am2 = 1.0 - xn[1];
  double ap3 = 1.0 + xn[2];
  double am3 = 1.0 - xn[2];

  // Compute for ( - , - ) values
  {
    double c1 = 0.125*am1*am2 ;
    double c2 = 0.125*am2*am3 ;
    double c3 = 0.125*am1*am3 ;
    shp[0][0] = -c2 ;
    shp[0][1] =  c2 ;
    shp[1][0] = -c3 ;
    shp[1][3] =  c3 ;
    shp[2][0] = -c1 ;
    shp[2][4] =  c1 ;
    shp[3][0] =  c1*am3 ;
    shp[3][4] =  c1*ap3 ;
  }

  // Compute for ( + , + ) values
  {
    double c1 = 0.125*ap1*ap2 ;
    double c2 = 0.125*ap2*ap3 ;
    double c3 = 0.125*ap1*ap3 ;
    shp[0][7] = -c2 ;
    shp[0][6] =  c2 ;
    shp[1][5] = -c3 ;
    shp[1][6] =  c3 ;
    shp[2][2] = -c1 ;
    shp[2][6] =  c1 ;
    shp[3][2] =  c1*am3 ;
    shp[3][6] =  c1*ap3 ;
  }

  // Compute for ( - , + ) values
  {
    double c1 = 0.125*am1*ap2 ;
    double c2 = 0.125*am2*ap3 ;
    double c3 = 0.125*am1*ap3 ;
    shp[0][4] = -c2 ;
    shp[0][5] =  c2 ; 
    shp[1][4] = -c3 ;
    shp[1][7] =  c3 ;
    shp[2][3] = -c1 ;
    shp[2][7] =  c1 ;
    shp[3][3] =  c1*am3 ;
    shp[3][7] =  c1*ap3 ;
  }
  // Compute for ( + , - ) values
  {
    double c1 = 0.125*ap1*am2 ;
    double c2 = 0.125*ap2*am3 ;
    double c3 = 0.125*ap1*am3 ;
    shp[0][3] = -c2 ;
    shp[0][2] =  c2 ;
    shp[1][1] = -c3 ;
    shp[1][2] =  c3 ;
    shp[2][1] = -c1 ;
    shp[2][5] =  c1 ;
    shp[3][1] =  c1*am3 ;
    shp[3][5] =  c1*ap3 ;
  }

  //
  // Compute jacobian transformation
  //

  double xs[3][3];
  for (int j=0; j<3; j++ ) {

    xs[j][0]  = ( xl[j][1] - xl[j][0] )*shp[0][1]
              + ( xl[j][2] - xl[j][3] )*shp[0][2]
              + ( xl[j][5] - xl[j][4] )*shp[0][5]
              + ( xl[j][6] - xl[j][7] )*shp[0][6];

    xs[j][1]  = ( xl[j][2] - xl[j][1] )*shp[1][2]
              + ( xl[j][3] - xl[j][0] )*shp[1][3]
              + ( xl[j][6] - xl[j][5] )*shp[1][6]
              + ( xl[j][7] - xl[j][4] )*shp[1][7];

    xs[j][2]  = ( xl[j][4] - xl[j][0] )*shp[2][4]
              + ( xl[j][5] - xl[j][1] )*shp[2][5]
              + ( xl[j][6] - xl[j][2] )*shp[2][6]
              + ( xl[j][7] - xl[j][3] )*shp[2][7];

  }  

  // Compute adjoint to jacobian

  double ad[3][3];
  ad[0][0] = xs[1][1]*xs[2][2] - xs[1][2]*xs[2][1] ;
  ad[0][1] = xs[2][1]*xs[0][2] - xs[2][2]*xs[0][1] ;
  ad[0][2] = xs[0][1]*xs[1][2] - xs[0][2]*xs[1][1] ;

  ad[1][0] = xs[1][2]*xs[2][0] - xs[1][0]*xs[2][2] ;
  ad[1][1] = xs[2][2]*xs[0][0] - xs[2][0]*xs[0][2] ;
  ad[1][2] = xs[0][2]*xs[1][0] - xs[0][0]*xs[1][2] ;

  ad[2][0] = xs[1][0]*xs[2][1] - xs[1][1]*xs[2][0] ;
  ad[2][1] = xs[2][0]*xs[0][1] - xs[2][1]*xs[0][0] ; 
  ad[2][2] = xs[0][0]*xs[1][1] - xs[0][1]*xs[1][0] ;

  // Compute determinant of jacobian

  xsj  = xs[0][0]*ad[0][0] + xs[0][1]*ad[1][0] + xs[0][2]*ad[2][0] ;
  double rxsj = 1.0/xsj ;

  // Compute jacobian inverse

  for (int j=0; j<3; j++) {
    for (int i=0; i<3; i++) 
      xs[i][j] = ad[i][j]*rxsj ;
  }


  // Compute derivatives with repect to global coords.

  for (int k=0; k<8; k++) {

    double c1 = shp[0][k]*xs[0][0] + shp[1][k]*xs[1][0] + shp[2][k]*xs[2][0] ;
    double c2 = shp[0][k]*xs[0][1] + shp[1][k]*xs[1][1] + shp[2][k]*xs[2][1] ;
    double c3 = shp[0][k]*xs[0][2] + shp[1][k]*xs[1][2] + shp[2][k]*xs[2][2] ;

    shp[0][k] = c1 ;
    shp[1][k] = c2 ;
    shp[2][k] = c3 ;
  }

  return;
}
