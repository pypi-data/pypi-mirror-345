#ifndef STLS_HPP
#define STLS_HPP

#include "input.hpp"
#include "numerics.hpp"
#include "rpa.hpp"
#include <cmath>
#include <vector>

// -----------------------------------------------------------------
// Solver for the STLS scheme
// -----------------------------------------------------------------

class Stls : public Rpa {

public:

  // Constructors
  Stls(const StlsInput &in_, const bool verbose_);
  explicit Stls(const StlsInput &in_)
      : Stls(in_, true) {}
  // Compute stls scheme
  int compute();
  // Getters
  const StlsInput &getInput() const { return in; }
  double getError() const { return computeError(); }

protected:

  // Static local field correction to use during the iterations
  std::vector<double> slfcNew;
  // Compute static local field correction
  void computeSlfc();
  // Iterations to solve the stls scheme
  void doIterations();
  void initialGuess();
  bool initialGuessFromInput();
  double computeError() const;
  void updateSolution();

private:

  // Input parameters
  StlsInput in;
};

namespace StlsUtil {

  // -----------------------------------------------------------------
  // Classes for the static local field correction
  // -----------------------------------------------------------------

  class SlfcBase {

  protected:

    // Constructor
    SlfcBase(const double &x_,
             const double &yMin_,
             const double &yMax_,
             std::shared_ptr<Interpolator1D> ssfi_)
        : x(x_),
          yMin(yMin_),
          yMax(yMax_),
          ssfi(ssfi_) {}
    // Wave-vector
    const double x;
    // Integration limits
    const double yMin;
    const double yMax;
    // Static structure factor interpolator
    const std::shared_ptr<Interpolator1D> ssfi;
    // Compute static structure factor
    double ssf(const double &y) const;
  };

  class Slfc : public SlfcBase {

  public:

    // Constructor
    Slfc(const double &x_,
         const double &yMin_,
         const double &yMax_,
         std::shared_ptr<Interpolator1D> ssfi_,
         std::shared_ptr<Integrator1D> itg_)
        : SlfcBase(x_, yMin_, yMax_, ssfi_),
          itg(itg_) {}
    // Get result of integration
    double get() const;

  private:

    // Integrator object
    const std::shared_ptr<Integrator1D> itg;
    // Integrand
    double integrand(const double &y) const;
  };

} // namespace StlsUtil

#endif
