import AppKit
import CoreImage
import Foundation
let dir=URL(fileURLWithPath:CommandLine.arguments[1],isDirectory:true)
let bg=CIImage(contentsOf:URL(fileURLWithPath:"/Users/USER/.codex/generated_images/01a16319-d848-71d0-95e1-72970644c800/exec-a7a991f6-6602-4866-86c4-faf1fd0502ee.png"))!
let photo=CIImage(contentsOf:URL(fileURLWithPath:"/Users/USER/Downloads/微信图片_20261029092153_362_2.jpg"),options:[.applyOrientationProperty:true])!
let w=bg.extent.width,h=bg.extent.height
let scaled=photo.transformed(by:CGAffineTransform(scaleX:w/photo.extent.width,y:h/photo.extent.height))
let mask=NSImage(size:NSSize(width:w,height:h));mask.lockFocus();NSColor.black.setFill();NSRect(x:0,y:0,width:w,height:h).fill();NSColor.white.setFill()
NSBezierPath(roundedRect:NSRect(x:w*0.20,y:-h*0.1,width:w*0.69,height:h*0.92),xRadius:100,yRadius:100).fill();mask.unlockFocus()
let m=CIImage(data:mask.tiffRepresentation!)!.applyingFilter("CIGaussianBlur",parameters:[kCIInputRadiusKey:45]).cropped(to:bg.extent)
let blended=scaled.applyingFilter("CIBlendWithMask",parameters:[kCIInputBackgroundImageKey:bg,kCIInputMaskImageKey:m])
let ctx=CIContext();let rep=NSBitmapImageRep(cgImage:ctx.createCGImage(blended,from:bg.extent)!)
try rep.representation(using:.jpeg,properties:[.compressionFactor:0.96])!.write(to:dir.appendingPathComponent("第二张_手持斜角_验证.jpg"))
