import AppKit
import CoreImage
import ImageIO
import UniformTypeIdentifiers
let source = CIImage(contentsOf: URL(fileURLWithPath: "实拍原件.jpg"), options: [.applyOrientationProperty: true])!
let w: CGFloat = 1368, h: CGFloat = 1824
let photo = source.transformed(by: CGAffineTransform(scaleX: w/source.extent.width, y: h/source.extent.height))
let bg0 = CIImage(contentsOf: URL(fileURLWithPath: "背景.png"))!
let bg = bg0.transformed(by: CGAffineTransform(scaleX: w/bg0.extent.width, y: h/bg0.extent.height))
let mask = NSImage(size: NSSize(width:w,height:h)); mask.lockFocus()
NSColor.black.setFill(); NSRect(x:0,y:0,width:w,height:h).fill()
NSColor.white.setFill(); NSBezierPath(roundedRect:NSRect(x:110,y:560,width:1120,height:640),xRadius:120,yRadius:120).fill()
mask.unlockFocus()
let maskCI = CIImage(data:mask.tiffRepresentation!)!.applyingFilter("CIGaussianBlur", parameters:[kCIInputRadiusKey:24]).cropped(to:CGRect(x:0,y:0,width:w,height:h))
let combined = photo.applyingFilter("CIBlendWithMask",parameters:[kCIInputBackgroundImageKey:bg,kCIInputMaskImageKey:maskCI])
let context=CIContext(); let cs=CGColorSpace(name:CGColorSpace.sRGB)!
let data=context.jpegRepresentation(of:combined,colorSpace:cs,options:[kCGImageDestinationLossyCompressionQuality as CIImageRepresentationOption:0.95])!
try data.write(to:URL(fileURLWithPath:"实拍主体_候选.jpg"))
