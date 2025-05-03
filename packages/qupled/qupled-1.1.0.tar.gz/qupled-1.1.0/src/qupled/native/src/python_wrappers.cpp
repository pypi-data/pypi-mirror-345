#include "python_wrappers.hpp"
#include "python_util.hpp"

using namespace std;

// -----------------------------------------------------------------
// PyInput
// -----------------------------------------------------------------

bn::ndarray PyInput::getChemicalPotentialGuess(Input &in) {
  return pythonUtil::toNdArray(in.getChemicalPotentialGuess());
}

void PyInput::setChemicalPotentialGuess(Input &in, const bp::list &muGuess) {
  in.setChemicalPotentialGuess(pythonUtil::toVector(muGuess));
}

// -----------------------------------------------------------------
// PyStlsGuess
// -----------------------------------------------------------------

bn::ndarray PyStlsGuess::getWvg(const StlsInput::Guess &guess) {
  return pythonUtil::toNdArray(guess.wvg);
}

bn::ndarray PyStlsGuess::getSlfc(const StlsInput::Guess &guess) {
  return pythonUtil::toNdArray(guess.slfc);
}

void PyStlsGuess::setWvg(StlsInput::Guess &guess, const bn::ndarray &wvg) {
  guess.wvg = pythonUtil::toVector(wvg);
}

void PyStlsGuess::setSlfc(StlsInput::Guess &guess, const bn::ndarray &slfc) {
  guess.slfc = pythonUtil::toVector(slfc);
}

// -----------------------------------------------------------------
// PyVSInput
// -----------------------------------------------------------------

bn::ndarray PyVSInput::getAlphaGuess(VSInput &in) {
  return pythonUtil::toNdArray(in.getAlphaGuess());
}

void PyVSInput::setAlphaGuess(VSInput &in, const bp::list &alphaGuess) {
  in.setAlphaGuess(pythonUtil::toVector(alphaGuess));
}

// -----------------------------------------------------------------
// PyFreeEnergyIntegrand
// -----------------------------------------------------------------

bn::ndarray
PyFreeEnergyIntegrand::getGrid(const VSStlsInput::FreeEnergyIntegrand &fxc) {
  return pythonUtil::toNdArray(fxc.grid);
}

bn::ndarray PyFreeEnergyIntegrand::getIntegrand(
    const VSStlsInput::FreeEnergyIntegrand &fxc) {
  return pythonUtil::toNdArray2D(fxc.integrand);
}

void PyFreeEnergyIntegrand::setGrid(VSStlsInput::FreeEnergyIntegrand &fxc,
                                    const bn::ndarray &grid) {
  fxc.grid = pythonUtil::toVector(grid);
}

void PyFreeEnergyIntegrand::setIntegrand(VSStlsInput::FreeEnergyIntegrand &fxc,
                                         const bn::ndarray &integrand) {
  fxc.integrand = pythonUtil::toDoubleVector(integrand);
}

// -----------------------------------------------------------------
// PyQstlsGuess
// -----------------------------------------------------------------

bn::ndarray PyQstlsGuess::getWvg(const QstlsInput::Guess &guess) {
  return pythonUtil::toNdArray(guess.wvg);
}

bn::ndarray PyQstlsGuess::getSsf(const QstlsInput::Guess &guess) {
  return pythonUtil::toNdArray(guess.ssf);
}

bn::ndarray PyQstlsGuess::getAdr(const QstlsInput::Guess &guess) {
  return pythonUtil::toNdArray2D(guess.adr);
}

int PyQstlsGuess::getMatsubara(const QstlsInput::Guess &guess) {
  return guess.matsubara;
}

void PyQstlsGuess::setWvg(QstlsInput::Guess &guess, const bn::ndarray &wvg) {
  guess.wvg = pythonUtil::toVector(wvg);
}

void PyQstlsGuess::setSsf(QstlsInput::Guess &guess, const bn::ndarray &ssf) {
  guess.ssf = pythonUtil::toVector(ssf);
}

void PyQstlsGuess::setAdr(QstlsInput::Guess &guess, const bn::ndarray &adr) {
  if (adr.shape(0) == 0) { return; }
  guess.adr = pythonUtil::toVector2D(adr);
}

void PyQstlsGuess::setMatsubara(QstlsInput::Guess &guess, const int matsubara) {
  guess.matsubara = matsubara;
}

// -----------------------------------------------------------------
// PyRpa
// -----------------------------------------------------------------

Input pyHF::getInput(const HF &hf) { return hf.getInput(); }

bn::ndarray pyHF::getIdr(const HF &hf) {
  return pythonUtil::toNdArray2D(hf.getIdr());
}

bn::ndarray pyHF::getRdf(const HF &hf, const bn::ndarray &r) {
  return pythonUtil::toNdArray(hf.getRdf(pythonUtil::toVector(r)));
}

bn::ndarray pyHF::getSdr(const HF &hf) {
  return pythonUtil::toNdArray(hf.getSdr());
}

bn::ndarray pyHF::getSlfc(const HF &hf) {
  return pythonUtil::toNdArray(hf.getSlfc());
}

bn::ndarray pyHF::getSsf(const HF &hf) {
  return pythonUtil::toNdArray(hf.getSsf());
}

bn::ndarray pyHF::getWvg(const HF &hf) {
  return pythonUtil::toNdArray(hf.getWvg());
}

double pyHF::getUInt(const HF &hf) { return hf.getUInt(); }

// -----------------------------------------------------------------
// PyStls
// -----------------------------------------------------------------

int PyStls::compute(Stls &stls) { return stls.compute(); }

StlsInput PyStls::getInput(const Stls &stls) { return stls.getInput(); }

double PyStls::getError(const Stls &stls) { return stls.getError(); }

// -----------------------------------------------------------------
// PyStlsIet
// -----------------------------------------------------------------

int PyStlsIet::compute(StlsIet &stlsiet) { return stlsiet.compute(); }

bn::ndarray PyStlsIet::getBf(const StlsIet &stlsiet) {
  return pythonUtil::toNdArray(stlsiet.getBf());
}

// -----------------------------------------------------------------
// PyVSStls
// -----------------------------------------------------------------

int PyVSStls::compute(VSStls &vsstls) { return vsstls.compute(); }

VSStlsInput PyVSStls::getInput(const VSStls &vsstls) {
  return vsstls.getInput();
}

double PyVSStls::getError(const VSStls &vsstls) {
  // NOTE: This is just a place-holder, getError is not yet implemented in
  // VSStls
  if (vsstls.getFreeEnergyIntegrand().empty()) { return -1; }
  return -1;
}

double PyVSStls::getAlpha(const VSStls &vsstls) { return vsstls.getAlpha(); }

bn::ndarray PyVSStls::getFreeEnergyIntegrand(const VSStls &vsstls) {
  return pythonUtil::toNdArray2D(vsstls.getFreeEnergyIntegrand());
}

bn::ndarray PyVSStls::getFreeEnergyGrid(const VSStls &vsstls) {
  return pythonUtil::toNdArray(vsstls.getFreeEnergyGrid());
}

// -----------------------------------------------------------------
// PyQstls
// -----------------------------------------------------------------

int PyQstls::compute(Qstls &qstls) { return qstls.compute(); }

QstlsInput PyQstls::getInput(const Qstls &qstls) { return qstls.getInput(); }

double PyQstls::getError(const Qstls &qstls) { return qstls.getError(); }

bn::ndarray PyQstls::getAdr(const Qstls &qstls) {
  return pythonUtil::toNdArray2D(qstls.getAdr());
}

// -----------------------------------------------------------------
// PyQstlsIet
// -----------------------------------------------------------------

int PyQstlsIet::compute(QstlsIet &qstlsiet) { return qstlsiet.compute(); }

bn::ndarray PyQstlsIet::getBf(const QstlsIet &qstlsiet) {
  return pythonUtil::toNdArray(qstlsiet.getBf());
}

// -----------------------------------------------------------------
// PyQVSStls
// -----------------------------------------------------------------

int PyQVSStls::compute(QVSStls &qvsstls) { return qvsstls.compute(); }

QVSStlsInput PyQVSStls::getInput(const QVSStls &qvsstls) {
  return qvsstls.getInput();
}

double PyQVSStls::getError(const QVSStls &qvsstls) {
  // NOTE: This is just a place-holder, getError is not yet implemented in
  // QVSStls
  if (qvsstls.getFreeEnergyIntegrand().empty()) { return -1; }
  return -1;
}

double PyQVSStls::getAlpha(const QVSStls &qvsstls) {
  return qvsstls.getAlpha();
}

bn::ndarray PyQVSStls::getAdr(const QVSStls &qvsstls) {
  return pythonUtil::toNdArray2D(qvsstls.getAdr());
}

bn::ndarray PyQVSStls::getFreeEnergyIntegrand(const QVSStls &qvsstls) {
  return pythonUtil::toNdArray2D(qvsstls.getFreeEnergyIntegrand());
}

bn::ndarray PyQVSStls::getFreeEnergyGrid(const QVSStls &qvsstls) {
  return pythonUtil::toNdArray(qvsstls.getFreeEnergyGrid());
}

// -----------------------------------------------------------------
// PyThermo
// -----------------------------------------------------------------

bn::ndarray PyThermo::computeRdf(const bn::ndarray &rIn,
                                 const bn::ndarray &wvgIn,
                                 const bn::ndarray &ssfIn) {
  const vector<double> &r = pythonUtil::toVector(rIn);
  const vector<double> &wvg = pythonUtil::toVector(wvgIn);
  const vector<double> &ssf = pythonUtil::toVector(ssfIn);
  return pythonUtil::toNdArray(thermoUtil::computeRdf(r, wvg, ssf));
}

double PyThermo::computeInternalEnergy(const bn::ndarray &wvgIn,
                                       const bn::ndarray &ssfIn,
                                       const double &coupling) {
  const vector<double> &wvg = pythonUtil::toVector(wvgIn);
  const vector<double> &ssf = pythonUtil::toVector(ssfIn);
  return thermoUtil::computeInternalEnergy(wvg, ssf, coupling);
}

double PyThermo::computeFreeEnergy(const bn::ndarray &gridIn,
                                   const bn::ndarray &rsuIn,
                                   const double &coupling) {
  const vector<double> &grid = pythonUtil::toVector(gridIn);
  const vector<double> &rsu = pythonUtil::toVector(rsuIn);
  return thermoUtil::computeFreeEnergy(grid, rsu, coupling);
}

// -----------------------------------------------------------------
// PyDatabaseInfo
// -----------------------------------------------------------------

string PyDatabaseInfo::getName(const DatabaseInfo &db) { return db.name; }

string PyDatabaseInfo::getRunTableName(const DatabaseInfo &db) {
  return db.runTableName;
}

int PyDatabaseInfo::getRunId(const DatabaseInfo &db) { return db.runId; }

void PyDatabaseInfo::setName(DatabaseInfo &db, const string &name) {
  db.name = name;
}

void PyDatabaseInfo::setRunTableName(DatabaseInfo &db,
                                     const string &runTableName) {
  db.runTableName = runTableName;
}

void PyDatabaseInfo::setRunId(DatabaseInfo &db, const int runId) {
  db.runId = runId;
}