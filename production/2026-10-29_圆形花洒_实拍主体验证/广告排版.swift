import AppKit
import Foundation
let dir=URL(fileURLWithPath:CommandLine.arguments[1],isDirectory:true)
let img=NSImage(contentsOf:dir.appendingPathComponent("实拍主体_暖白合成验证.jpg"))!
let w=img.size.width,h=img.size.height
let canvas=NSImage(size:NSSize(width:w,height:h));canvas.lockFocus()
img.draw(in:NSRect(x:0,y:0,width:w,height:h))
let dark=NSColor(calibratedRed:0.29,green:0.15,blue:0.08,alpha:1)
let font=NSFont(name:"PingFangSC-Semibold",size:64) ?? NSFont.boldSystemFont(ofSize:64)
("三档\n出水" as NSString).draw(in:NSRect(x:30,y:h-390,width:210,height:190),withAttributes:[.font:font,.foregroundColor:dark])
canvas.unlockFocus();let rep=NSBitmapImageRep(data:canvas.tiffRepresentation!)!
try rep.representation(using:.jpeg,properties:[.compressionFactor:0.95])!.write(to:dir.appendingPathComponent("实拍主体_统一画面广告验证.jpg"))
