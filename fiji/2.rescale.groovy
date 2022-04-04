//@File(label="Input directory", description="Select the directory with input images", style="directory") inputDir

import ij.IJ
import ij.ImagePlus
import ij.Prefs
import ij.WindowManager
import ij.process.ImageProcessor
import ij.gui.GenericDialog


import loci.plugins.BF

import java.io.File
import java.lang.Double
import java.nio.file.Paths

import groovy.io.FileType
import groovy.time.TimeCategory 
import groovy.time.TimeDuration

import loci.plugins.BF
import loci.formats.ChannelSeparator
import loci.formats.FormatException
import loci.formats.IFormatReader
import loci.formats.meta.IMetadata
import loci.formats.MetadataTools

import loci.common.Region
import loci.plugins.in.ImporterOptions

import loci.plugins.util.ImageProcessorReader
import loci.plugins.util.LociPrefs
import loci.common.Region

import java.awt.Rectangle
import java.io.File
import java.lang.Double
import java.nio.file.Paths
import java.util.Collections

import static groovy.io.FileType.FILES

new File(Paths.get(inputDir.getAbsolutePath(), 'results').toString()).mkdir()
resultPath=Paths.get(inputDir.getAbsolutePath(), 'results').toString()


maxWidth=-1
maxHeight=-1

inputDir.eachFileRecurse(FILES) {
  if(it.name.endsWith('.tif')) {

    filePath=it.getAbsolutePath()
    id=Paths.get(filePath).toString()
    ImageProcessorReader r = new ImageProcessorReader(new ChannelSeparator(LociPrefs.makeImageReader())) 
    omeMeta = MetadataTools.createOMEXMLMetadata()
    r.setMetadataStore(omeMeta)
    omeMeta = MetadataTools.createOMEXMLMetadata()
    r.setMetadataStore(omeMeta)
    r.setId(id)
    series=r.getSeriesCount()   
    for(int s=0; s<series; s++)
    {
      r.setSeries(s) 
      width=r.getSizeX()
      height=r.getSizeY()  
      if(maxWidth<width)
        maxWidth=width
      if(maxHeight<height)
        maxHeight=height
      println(width+','+height)
    }
/*
    
    fileName=it.name
    id=Paths.get(inputDir.getAbsolutePath(), fileName).toString()
    def baseName=fileName[0..-5]
    ImagePlus[] imps = BF.openImagePlus(id)
    imp=imps[0]
    if(maxWidth<imp.getWidth())
      maxWidth=imp.getWidth()
    if(maxHeight<imp.getHeight())
      maxHeight=imp.getHeight()
*/
  }
}

inputDir.eachFileRecurse(FILES) {
  if(it.name.endsWith('.tif')) {
    fileName=it.name
    id=Paths.get(inputDir.getAbsolutePath(), fileName).toString()
    def baseName=fileName[0..-5]
    ImagePlus[] imps = BF.openImagePlus(id)
    imp=imps[0]
    IJ.run(imp, "Canvas Size...", "width="+maxWidth+" height="+maxHeight+" position=Center")
    IJ.saveAs(imp, 'TIF', Paths.get(resultPath, baseName+'.tif').toString())

//from io.scif.img import ImgOpener, ImgSaver
//from net.imglib2.img import ImagePlusAdapter 
//    img = ImagePlusAdapter.wrap(imp)
//    saver = ImgSaver()
//    saver.saveImg("/home/daniel/Desktop/cleared.ome.tif",img) //btif
  }
}
gd = new GenericDialog('Rescaling Done')
gd.addMessage('Rescaling the image canvas is Done!')
gd.showDialog()
