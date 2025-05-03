#pragma once
#include <cmath>
#include <VectorND.h>

struct Versor {
    Vector3D vector;
    double   scalar;

    template <typename Vec3T>
    inline Vec3T 
    rotate(const Vec3T& u) const {
        return u + 2.0 * vector.cross( scalar*u + vector.cross(u) );
    }

    inline Versor conjugate() const {
        Versor c;
        c.scalar = scalar; 
        c.vector = -1.0*vector;  // element-wise negation
        return c;
    }

    inline Versor conj_mult(const Versor& other) const 
    {
        // Equivalent to R_IJ = R_I.T @ R_J, 
        // i.e.  q_IJ = conj(q_I)*q_J.
        Versor out;
        out.scalar = scalar * other.scalar + vector.dot(other.vector);
        out.vector = (other.vector * scalar) - (vector * other.scalar) - vector.cross(other.vector);
        return out;
    }

    inline Versor mult_conj(const Versor& other) const 
    {
        // Equivalent to R_IJ = R_I @ R_J^T, 
        // i.e.  q_IJ = q_I * conj(q_J).

        // Versor out = *this;
        // out *= other.conjugate();
        // return out;

        Versor out;
        out.scalar = scalar * other.scalar + vector.dot(other.vector);
        out.vector =      (vector    * other.scalar)
                       - (other.vector * scalar)
                       - vector.cross(other.vector);
        return out;
    }

    template<typename Vec3T>
    static inline Versor
    from_vector(const Vec3T  &theta)
    {

        double t = 0.0; // theta.norm();
        for (int i=0; i<3; i++)
            t += theta[i]*theta[i];
        t = std::sqrt(t);

        Versor q;
        if (t == 0)
            q.vector.zero();

        else {
            const double factor = std::sin(t*0.5) / t;
            for (int i = 0; i < 3; i++)
                q.vector[i] = theta[i] * factor;
        }

        q.scalar = std::cos(t*0.5);

        return q;
    }

//   inline Versor &operator*= (const Versor& b)
//   {
//       vector[0] = scalar*b.vector[0] + vector[0]*b.scalar + vector[1]*b.vector[2] - vector[2]*b.vector[1];
//       vector[1] = scalar*b.vector[1] + vector[1]*b.scalar + vector[2]*b.vector[0] - vector[0]*b.vector[2];
//       vector[2] = scalar*b.vector[2] + vector[2]*b.scalar + vector[0]*b.vector[1] - vector[1]*b.vector[0];
//       scalar =    scalar*b.scalar - vector[0]*b.vector[0] - vector[1]*b.vector[1] - vector[2]*b.vector[2];
//       return *this;
//   }
};

#if 1
inline Versor
operator*(const Versor &qa, const Versor &qb)
{
    const double qa0 = qa.vector[0],
                 qa1 = qa.vector[1],
                 qa2 = qa.vector[2],
                 qa3 = qa.scalar,
                 qb0 = qb.vector[0],
                 qb1 = qb.vector[1],
                 qb2 = qb.vector[2],
                 qb3 = qb.scalar;

    // Calculate the dot product qa.qb
    const double qaTqb = qa0*qb0 + qa1*qb1 + qa2*qb2;

    // Calculate the cross-product qa x qb
    const double
      qaxqb0 = qa1*qb2 - qa2*qb1,
      qaxqb1 = qa2*qb0 - qa0*qb2,
      qaxqb2 = qa0*qb1 - qa1*qb0;

    // Calculate the quaternion product
    Versor q12;
    q12.vector[0] = qa3*qb0 + qb3*qa0 - qaxqb0;
    q12.vector[1] = qa3*qb1 + qb3*qa1 - qaxqb1;
    q12.vector[2] = qa3*qb2 + qb3*qa2 - qaxqb2;
    q12.scalar = qa3*qb3 - qaTqb;
    return q12;
}
#else
inline Versor 
operator* (const Versor& a, const Versor& b)
{
    return Versor{{
        a[0]*b[0] - a[1]*b[1] - a[2]*b[2] - a[3]*b[3],
        a[0]*b[1] + a[1]*b[0] + a[2]*b[3] - a[3]*b[2],
        a[0]*b[2] + a[2]*b[0] + a[3]*b[1] - a[1]*b[3],
        a[0]*b[3] + a[3]*b[0] + a[1]*b[2] - a[2]*b[1]
    }};
}
#endif