import Cocoa
import Vision
import CoreImage
import ImageIO
let src = URL(fileURLWithPath: CommandLine.arguments[1])
let output = URL(fileURLWithPath: CommandLine.arguments[2])
let request = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(url: src, options: [:])
try handler.perform([request])
guard let result = request.results?.first else { fatalError("no foreground") }
let buffer = try result.generateScaledMaskForImage(forInstances: result.allInstances, from: handler)
let ci = CIImage(cvPixelBuffer: buffer)
let ctx = CIContext()
let cg = ctx.createCGImage(ci, from: ci.extent)!
let rep = NSBitmapImageRep(cgImage: cg)
try rep.representation(using: .png, properties: [:])!.write(to: output)
