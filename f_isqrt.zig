const std = @import("std");
const math = std.math;

const x1 = 1.0 / math.ln(2.0) - 1.0;
const c_log2p1: f32 = (0.0 + (math.log2(1.0 + x1) - x1)) / 2.0;
// fast log2(1 + x) for x in [0; 1]
pub fn f_log2p1(x: f32) f32 {
  return x + c_log2p1;
}

const c_isqrt: i32 = math.round((3 << 22) * (127.0 - f_log2p1(0)));
// fast 1/sqrt(x) for x in [0; 1] (less accurate near 0)
pub fn f_isqrt(x: f32) f32 {
  var half_x = x * 0.5;
  // Algorithm
  var i = @bitCast(i32, x); // i = log2(x)
  i = -(i >> 1) + c_isqrt; // i = -1/2 log2(x) = log2(1/sqrt(x)) // TODO: how does one generalize this to other powers?
  var y = @bitCast(f32, i); // y = 2^i = 1/sqrt(x)
  // Newtons method
  y = y * (1.5 - (half_x * y * y)); // 1st iteration
  //y = y * (1.5 - (half_x * y * y)); // 2nd iteration
  return y;
}

pub fn main() !void {
  const stdout = std.io.getStdOut().writer();
  std.log.debug("{}\n", .{c_log2p1});
  
  const X = [_]f32{0, 0.1, x1, 1};
  for(X) |x| {
    try stdout.print("{} {}\n", .{f_isqrt(x), 1 / @sqrt(x)});
  }
}
