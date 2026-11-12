import AppKit
import CoreImage
import Foundation
let dir=URL(fileURLWithPath:CommandLine.arguments[1],isDirectory:true)
let src=CIImage(contentsOf:dir.appendingPathComponent("第二张_手持斜角_验证.jpg"))!
let r=CGRect(x:0,y:90,width:src.extent.width,height:src.extent.height-90)
let cg=CIContext().createCGImage(src,from:r)!
let img=NSImage(cgImage:cg,size:NSSize(width:r.width,height:r.height))
let canvas=NSImage(size:img.size);canvas.lockFocus();img.draw(in:NSRect(origin:.zero,size:img.size))
let font=NSFont(name:"PingFangSC-Semibold",size:62) ?? NSFont.boldSystemFont(ofSize:62)
let color=NSColor(calibratedRed:0.29,green:0.15,blue:0.08,alpha:1)
("手持花洒" as NSString).draw(in:NSRect(x:50,y:r.height-280,width:400,height:100),withAttributes:[.font:font,.foregroundColor:color])
canvas.unlockFocus();let out=NSBitmapImageRep(data:canvas.tiffRepresentation!)!
try out.representation(using:.jpeg,properties:[.compressionFactor:0.96])!.write(to:dir.appendingPathComponent("第二张_手持斜角_暖白.jpg"))
