const std = @import("std");
const math = std.math;

pub fn main() !void {
  const stdout = std.io.getStdOut().writer();
  std.log.debug("{}\n", .{u});
  const X = [_]f32{0, 0.1, root, 1};
  for(X) |x| {
    try stdout.print("{} {}\n", .{1 / @sqrt(x), Q_rsqrt(x)});
  }
}

const u: f64 = comptime {
  //return 0.0430 // claimed by video (correctly)
  //return 0.0450465 // used by video
  //return 0.057304959111; // by mean value
  return (math.log2(1+root) - root) / 2.0; // by minimizing maximum value = 0.043035666028
};
const root: f32 = comptime 1/math.ln(2.0) - 1.0; // maximum of (log2(1+x) - x)

pub fn Q_log2p1(x: f32) f32 {
  // fast log2(1+x) for 0 <= x <= 1
  return x + u;
}

pub fn Q_rsqrt(x: f32) f32 {
  // fast inverse square root for 0 < x <= 1 (less accurate near 0)

  // Correction terms
  const c = comptime @floatToInt(i32, -3 * (1 << 22) * (u - 127.0));
  var x2 = x * 0.5;

  // Algorithm
  var i = @bitCast(i32, x); // i = log2(x)
  i = - (i >> 1); // i = -1/2 log2(x) = log2(1/sqrt(x))
  var y = @bitCast(f32, c+i); // c+i has the bits of 1/sqrt(x)

  // Newtons method
  y = y * (1.5 - (x2 * y * y)); // 1st iteration
  //y = y * (1.5 - (x2 * y * y)); // 2nd iteration

  return y;
}
