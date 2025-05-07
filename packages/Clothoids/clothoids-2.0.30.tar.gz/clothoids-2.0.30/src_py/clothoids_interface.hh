#include "Clothoids.hh"
#include "GenericContainer/GenericContainer.hh"
#include <array>
#include <string>
#include <utility>
#include <vector>

namespace clothoids
{

class ClothoidCurve
{
private:
  G2lib::ClothoidCurve clothoid_curve;

public:
  ClothoidCurve(std::string name = "") : clothoid_curve{name} {}

  ClothoidCurve(
    double const x0, double const y0, double const theta0, double const k, double const dk, double const L, std::string const &name
  )
      : clothoid_curve{x0, y0, theta0, k, dk, L, name}
  {
  }

  void
  build(double const x0, double const y0, double const theta0, double const k, double const dk, double const L)
  {
    this->clothoid_curve.build(x0, y0, theta0, k, dk, L);
  }

  int build_G1(
    double const x0,
    double const y0,
    double const theta0,
    double const x1,
    double const y1,
    double const theta1,
    double const tol = 1e-12
  )
  {
    return this->clothoid_curve.build_G1(x0, y0, theta0, x1, y1, theta1, tol);
  }

  double length() const { return this->clothoid_curve.length(); }

  std::pair<double, double> eval(double const s) const
  {
    double x{0.0};
    double y{0.0};

    this->clothoid_curve.eval(s, x, y);

    return {x, y};
  }

  std::pair<double, double> curvature_min_max() const
  {
    double kappa_min{0.0};
    double kappa_max{0.0};

    this->clothoid_curve.curvature_min_max(kappa_min, kappa_max);

    return {kappa_min, kappa_max};
  }

  double theta(double const s) const { return this->clothoid_curve.theta(s); }

  double theta_D(double const s) const { return this->clothoid_curve.theta_D(s); }

  double theta_DD(double const s) const { return this->clothoid_curve.theta_DD(s); }

  double theta_DDD(double const s) const { return this->clothoid_curve.theta_DDD(s); }

  // void set_gc(GC_namespace::GenericContainer const &gc) { gc.dump(std::cout); }
  //
  // GC_namespace::GenericContainer get_gc()
  // {
  //   GC_namespace::GenericContainer gc;
  //   gc["string"] = "Hello";
  //   gc["int"]    = 42;
  //   return gc;
  // }
};

class ClothoidList
{
private:
  G2lib::ClothoidList clothoid_list;

public:
  ClothoidList(std::string name = "") : clothoid_list{name} {}

  bool build_G1(std::vector<double> const &x, std::vector<double> const &y)
  {
    return this->clothoid_list.build_G1(x.size(), x.data(), y.data());
  }

  bool
  build_G1(std::vector<double> const &x, std::vector<double> const &y, std::vector<double> const &theta)
  {
    return this->clothoid_list.build_G1(x.size(), x.data(), y.data(), theta.data());
  }

  bool build(
    double const x0, double const y0, double const theta0, std::vector<double> const &s, std::vector<double> const &kappa
  )
  {
    return this->clothoid_list.build(x0, y0, theta0, s, kappa);
  }

  double length() const { return this->clothoid_list.length(); }

  void make_closed() { this->clothoid_list.make_closed(); }

  void make_open() { this->clothoid_list.make_open(); }

  std::pair<double, double> eval(double const s) const
  {
    double x{0.0};
    double y{0.0};

    this->clothoid_list.eval(s, x, y);

    return {x, y};
  }

  std::pair<std::vector<double>, std::vector<double>> eval(std::vector<double> const &s) const
  {
    std::vector<double> x, y;
    x.reserve(s.size());
    y.reserve(s.size());

    for (auto const &s_i : s)
    {
      double _x{0.0};
      double _y{0.0};

      this->clothoid_list.eval(s_i, _x, _y);

      x.push_back(_x);
      y.push_back(_y);
    }

    return std::make_pair(std::move(x), std::move(y));
  }

  std::pair<double, double> eval_ISO(double const s, double const offs) const
  {
    double x{0.0};
    double y{0.0};

    this->clothoid_list.eval_ISO(s, offs, x, y);

    return {x, y};
  }

  std::pair<std::vector<double>, std::vector<double>>
  eval_ISO(std::vector<double> const &s, double const offs) const
  {
    std::vector<double> x, y;
    x.reserve(s.size());
    y.reserve(s.size());

    for (auto const &s_i : s)
    {
      double _x{0.0};
      double _y{0.0};

      this->clothoid_list.eval_ISO(s_i, offs, _x, _y);

      x.push_back(_x);
      y.push_back(_y);
    }

    return std::make_pair(std::move(x), std::move(y));
  }

  std::pair<std::vector<double>, std::vector<double>>
  eval_ISO(std::vector<double> const &s, std::vector<double> const &offs) const
  {
    std::vector<double> x, y;
    x.reserve(s.size());
    y.reserve(s.size());

    for (size_t i{0}; i < s.size(); i++)
    {
      double _x{0.0};
      double _y{0.0};

      this->clothoid_list.eval_ISO(s.at(i), offs.at(i), _x, _y);

      x.push_back(_x);
      y.push_back(_y);
    }

    return std::make_pair(std::move(x), std::move(y));
  }

  std::array<double, 4> evaluate(double const s) const
  {
    double theta{0.0};
    double kappa{0.0};
    double x{0.0};
    double y{0.0};

    this->clothoid_list.evaluate(s, theta, kappa, x, y);

    return {theta, kappa, x, y};
  }

  double theta(double const s) const { return this->clothoid_list.theta(s); }

  double theta_D(double const s) const { return this->clothoid_list.theta_D(s); }

  double theta_DD(double const s) const { return this->clothoid_list.theta_DD(s); }

  double theta_DDD(double const s) const { return this->clothoid_list.theta_DDD(s); }

  std::pair<double, double> findST1(double const x, double const y) const
  {
    double s{0.0};
    double n{0.0};

    this->clothoid_list.findST1(x, y, s, n);

    return {s, n};
  }

  std::array<double, 5> closest_point_ISO(double const x, double const y) const
  {
    double _x{0.0};
    double _y{0.0};
    double _s{0.0};
    double _t{0.0};
    double _dst{0.0};

    this->clothoid_list.closest_point_ISO(x, y, _x, _y, _s, _t, _dst);

    return {_x, _y, _s, _t, _dst};
  }

  std::array<double, 5> closest_point_ISO(double const x, double const y, double const offset) const
  {
    double _x{0.0};
    double _y{0.0};
    double _s{0.0};
    double _t{0.0};
    double _dst{0.0};

    this->clothoid_list.closest_point_ISO(x, y, offset, _x, _y, _s, _t, _dst);

    return {_x, _y, _s, _t, _dst};
  }

  std::array<double, 6>
  closest_point_in_s_range_ISO(double const x, double const y, double const s_begin, double const s_end) const
  {
    double _x{0.0};
    double _y{0.0};
    double _s{0.0};
    double _t{0.0};
    double _dst{0.0};
    int _icurve{0};

    this->clothoid_list.closest_point_in_s_range_ISO(x, y, s_begin, s_end, _x, _y, _s, _t, _dst, _icurve);

    return {_x, _y, _s, _t, _dst, static_cast<double>(_icurve)};
  }
};

class G2solve3arc
{
private:
  G2lib::G2solve3arc g2solve3arc;

public:
  G2solve3arc() = default;

  int build(
    double x0,
    double y0,
    double theta0,
    double kappa0,
    double x1,
    double y1,
    double theta1,
    double kappa1,
    double Dmax = 0,
    double dmax = 0
  )
  {
    return this->g2solve3arc.build(x0, y0, theta0, kappa0, x1, y1, theta1, kappa1, Dmax, dmax);
  }

  int build_fixed_length(
    double const s0,
    double const x0,
    double const y0,
    double const theta0,
    double const kappa0,
    double const s1,
    double const x1,
    double const y1,
    double const theta1,
    double const kappa1
  )
  {
    return this->g2solve3arc.build_fixed_length(s0, x0, y0, theta0, kappa0, s1, x1, y1, theta1, kappa1);
  }

  double total_length() const { return this->g2solve3arc.total_length(); }

  double theta(double const s) const { return this->g2solve3arc.theta(s); }

  double theta_D(double const s) const { return this->g2solve3arc.theta_D(s); }

  double theta_DD(double const s) const { return this->g2solve3arc.theta_DD(s); }

  double theta_DDD(double const s) const { return this->g2solve3arc.theta_DDD(s); }

  double X(double const s) const { return this->g2solve3arc.X(s); }

  double Y(double const s) const { return this->g2solve3arc.Y(s); }

  std::array<double, 4> evaluate(double const s) const
  {
    double theta{0.0};
    double kappa{0.0};
    double x{0.0};
    double y{0.0};

    this->g2solve3arc.eval(s, theta, kappa, x, y);

    return {theta, kappa, x, y};
  }

  std::pair<double, double> eval(double const s) const
  {
    double x{0.0};
    double y{0.0};

    this->g2solve3arc.eval(s, x, y);

    return {x, y};
  }

  std::pair<std::vector<double>, std::vector<double>> eval(std::vector<double> const &s) const
  {
    std::vector<double> x;
    std::vector<double> y;
    x.reserve(s.size());
    y.reserve(s.size());

    for (auto const &s_i : s)
    {
      double _x{0.0};
      double _y{0.0};

      this->g2solve3arc.eval(s_i, _x, _y);

      x.push_back(_x);
      y.push_back(_y);
    }

    return std::make_pair(std::move(x), std::move(y));
  }

  std::pair<double, double> eval_D(double const s) const
  {
    double x{0.0};
    double y{0.0};

    this->g2solve3arc.eval_D(s, x, y);

    return {x, y};
  }

  std::pair<double, double> eval_DD(double const s) const
  {
    double x{0.0};
    double y{0.0};

    this->g2solve3arc.eval_DD(s, x, y);

    return {x, y};
  }

  std::pair<double, double> eval_DDD(double const s) const
  {
    double x{0.0};
    double y{0.0};

    this->g2solve3arc.eval_DDD(s, x, y);

    return {x, y};
  }
};

}; // namespace clothoids
