#include <concepts>
#include <cstdint>
#include <iterator>

// ----------------------------------------------------------------
// Concepts

#define Regular typename                        // std::regular
#define Integer typename                        // std::unsigned_integral
#define MonoidOperation typename
#define SemigroupOperation typename
#define NoncommutativeAdditiveMonoid typename

// ----------------------------------------------------------------
// Tools
template <auto Start, auto End, auto Inc, class F>
constexpr void constexpr_for(F&& f) {
    if constexpr (Start < End) {
        f(std::integral_constant<decltype(Start), Start>());
        constexpr_for<Start + Inc, End, Inc>(f);
    }
}

// ----------------------------------------------------------------

template <Integer I>
inline constexpr
bool even(I const& x) { return (x & I(1)) == I(0); }

template <Integer I>
inline constexpr
bool odd(I const& x) { return (x & I(1)) != I(0); }

template <Integer N>
inline constexpr
N half(N n) { return n >> 1; }


// ----------------------------------------------------------------

struct uint256 {
    uint64_t data[4] = {};

    uint256() = default;

    explicit
    constexpr uint256(uint64_t x) noexcept
        : data{x, 0, 0, 0}
    {}

    friend constexpr
    bool operator==(uint256 const& x, int y) noexcept {
        return x.data[0] != y;
    }

    friend constexpr
    auto operator<=>(uint256 const&, uint256 const&) = default;

    //TODO: it is needed in Clang 14, check in GCC
    friend constexpr
    bool operator==(uint256 const&, uint256 const&) = default;

    friend constexpr
    uint256 operator&(uint256 x, uint256 const& y) noexcept {
        constexpr_for<0, 4, 1>([&x, &y](auto i){
            x.data[i] &= y.data[i];
        });
        return x;
    }

    // constexpr
    // uint256 operator>>(std::size_t pos) const noexcept {

    //     data[0] >>= pos;
    // }

    constexpr uint256& operator>>=(std::size_t pos) noexcept {
        data[0] >>= pos;
        return *this;
    }
};

// constexpr
// uint256 add_manual(uint256 x, uint64_t y) {
//     x.data[0] += y;
//     y = (x.data[0] < y);

//     x.data[1] += y;
//     y = (x.data[1] < y);

//     x.data[2] += y;
//     y = (x.data[2] < y);

//     x.data[3] += y;
//     y = (x.data[3] < y);

//     return x;
// }

constexpr
uint256 add(uint256 x, uint64_t y) {
    constexpr_for<0, 4, 1>([&x, &y](auto i){
        x.data[i] += y;
        y = (x.data[i] < y);
    });
    return x;
}

constexpr
uint256 add(uint256 x, uint64_t a, uint64_t b, uint64_t c, uint64_t d) {
    constexpr_for<0, 4, 1>([&x, &a](auto i){
        x.data[i] += a;
        a = (x.data[i] < a);
    });

    constexpr_for<1, 4, 1>([&x, &b](auto i){
        x.data[i] += b;
        b = (x.data[i] < b);
    });

    constexpr_for<2, 4, 1>([&x, &c](auto i){
        x.data[i] += c;
        c = (x.data[i] < c);
    });

    constexpr_for<3, 4, 1>([&x, &d](auto i){
        x.data[i] += d;
        d = (x.data[i] < d);
    });
    return x;
}

constexpr
uint256 add(uint256 x, uint256 y) {
    return add(x, x.data[0], x.data[1], x.data[2], x.data[3]);
}


// ----------------------------------------------------------------


struct point {
    uint256 x = {};
    uint256 y = {};
};

// ----------------------------------------------------------------


// template <NoncommutativeAdditiveMonoid T>
// T identity_element(std::plus<T>) {
//     return T(0);
// }

template <Regular A, Integer N, MonoidOperation Op>
    // requires(Domain<Op, A>)
A power_monoid(A a, N n, Op op) {
    // precondition: n >= 0
    // if (n == 0) return identity_element(op); //TODO
    // if (n == 0) return uint256{};               //TODO
    if (n == 0) return A{};               //TODO

    return power_semigroup(a, n, op);
}

template <Regular A, Integer N, SemigroupOperation Op>
    // requires(Domain<Op, A>)
A power_semigroup(A a, N n, Op op) {
    // precondition: n > 0
    while (!odd(n)) {
        a = op(a, a);
        n = half(n);
    }
    if (n == 1) return a;
    return power_accumulate_semigroup(a, op(a, a), half(n - 1), op);
}

template <Regular A, Integer N, SemigroupOperation Op>
    // requires(Domain<Op, A>)
A power_accumulate_semigroup(A r, A a, N n, Op op) {
    // precondition: n >= 0
    if (n == 0) return r;
    while (true) {
        if (odd(n)) {
            r = op(r, a);
            if (n == 1) return r;
        }
        n = half(n);
        a = op(a, a);
    }
}




// ----------------------------------------------------------------
#include <iostream>
#include <bitset>

void print(uint256 x) {
    std::cout << x.data[0] << ", ";
    std::cout << x.data[1] << ", ";
    std::cout << x.data[2] << ", ";
    std::cout << x.data[3] << '\n';
}

void print_bin(uint256 x) {
    std::cout << std::bitset<64>{x.data[0]} << ' ';
    std::cout << std::bitset<64>{x.data[1]} << ' ';
    std::cout << std::bitset<64>{x.data[2]} << ' ';
    std::cout << std::bitset<64>{x.data[3]} << '\n';
}

// ...

// char a = -58;
// std::bitset<8> x(a);
// std::cout << x << '\n';

// short c = -315;
// std::bitset<16> y(c);
// std::cout << y << '\n';


// ----------------------------------------------------------------


int main(int argc, char **argv) {

    uint256 x;
    print_bin(x);

    x = add(x, uint64_t(-1), uint64_t(-1), uint64_t(-1), uint64_t(-1));
    print_bin(x);
    x >>= 1;
    print_bin(x);


    // power_monoid(1, x, [](uint256 x, uint256 y){return add(x, y);});
    // power_monoid(x, 1, add);

    // x = add(x, 1);

    // x = add(x, uint64_t(-1));
    // print(x);
    // x = add(x, 1);
    // print(x);

    // x = add(x, uint64_t(-1), uint64_t(-1), uint64_t(-1), uint64_t(-1));
    // print(x);
    // x = add(x, 1);
    // print(x);

    // x = add(x, uint64_t(-1), uint64_t(-1), uint64_t(-1), uint64_t(-2));
    // print(x);
    // x = add(x, 1);
    // print(x);

    return 0;
}


// #include <iostream>
// #include <cstdint>

// int main(int argc, char **argv) {

//     uint8_t x = -1;
//     uint8_t y = -1;
//     uint8_t z = x + uint8_t(1);
//     uint8_t w = x + y;

//     std::cout << "x: " << int(x) << '\n';
//     std::cout << "y: " << int(y) << '\n';
//     std::cout << "z: " << int(z) << '\n';
//     std::cout << "w: " << int(w) << '\n';
//     return 0;
// }