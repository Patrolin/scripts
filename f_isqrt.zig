// TODO: port this to a modern version of Zig
const std = @import("std");
const math = std.math;

const x1 = 1.0 / math.ln(2.0) - 1.0;
const log2p1_bias: f32 = -(0.0 + (math.log2(1.0 + x1) - x1)) / 2.0;
// fast log2(1 + x) for x in [0; 1]
pub fn f_log2p1(x: f32) f32 {
    return x - log2p1_bias;
}

// @bitCast(i32, x) = ~ (log2(x) + 127) * 2^23
const sqrt_bias: i32 = (127 * 1 << 22) - (127 * 1 << 23);
pub fn f_sqrt(x: f32) f32 {
    // 1/2 * log2(x) = log2(sqrt(x))
    var i = @bitCast(i32, x); // i = (log2(x) + 127) * 2^23
    i = i >> 1; // 1/2 i = (log2(sqrt(x)) * 2^23) + (1/2 * 127 * 2^23)
    i = i - sqrt_bias; // sqrt_bias = (1/2 * 127 * 2^23) - (127 * 2^23)
    var y = @bitCast(f32, i); // i = (log2(sqrt(x)) + 127) * 2^23
    return y; // y = sqrt(x)
}
// TODO: investigate assembly: https://www.codeproject.com/Articles/69941/Best-Square-Root-Method-Algorithm-Function-Precisi

pub const isqrt_bias: i32 = (-127 * 1 << 22) - (127 * 1 << 23);
pub fn f_isqrt(x: f32) f32 {
    var half_x = x * 0.5;

    // -1/2 * log2(x) = log2(1/sqrt(x))
    var i = @bitCast(i32, x); // i = (log2(x) + 127) * 2^23
    i = -(i >> 1); // -1/2 i = (log2(1/sqrt(x)) * 2^23) + (-1/2 * 127 * 2^23)
    i = i - isqrt_bias; // isqrt_bias = (-1/2 * 127 * 2^23) - (127 * 2^23)
    var y = @bitCast(f32, i); // i = (log2(1/sqrt(x)) + 127) * 2^23

    // Newtons method // https://www.youtube.com/watch?v=E24zUEKqgwQ
    y = y * (1.5 - (half_x * y * y)); // 1st iteration
    //y = y * (1.5 - (half_x * y * y)); // 2nd iteration
    return y; // y = 1/sqrt(x)
}

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    const X = [_]f32{ 0, 0.1, x1, 10 };
    for (X) |x| {
        stdout.print("{e:.2} {e:.2}\n", .{ f_sqrt(x), @sqrt(x) }) catch unreachable;
    }
    stdout.print("\n", .{}) catch unreachable;
    for (X) |x| {
        stdout.print("{e:.2} {e:.2}\n", .{ f_isqrt(x), 1 / @sqrt(x) }) catch unreachable;
    }
}
