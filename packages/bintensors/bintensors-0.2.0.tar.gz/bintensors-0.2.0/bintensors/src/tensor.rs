//! Module Containing the most important structures
use crate::lib::{BTreeMap, Cow, HashMap, String, ToString, Vec};
#[cfg(feature = "slice")]
use crate::slice::{InvalidSlice, SliceIterator, TensorIndexer};
use bincode::{Decode, Encode};
use digest::Digest;

#[cfg(feature = "std")]
use std::io::Write;
#[cfg(feature = "std")]
use std::path::Path;

const MIN_HEADER_SIZE: usize = 8;
const MAX_HEADER_SIZE: usize = 100_000_000;
const OFFSET: usize = 8;

/// Possible errors that could occur while reading
/// A Bintensor file.
#[derive(Debug)]
pub enum BinTensorError {
    /// The header is an invalid UTF-8 string and cannot be read.
    InvalidHeader,
    /// The header is large than 100Mo which is considered too large (Might evolve in the future).
    HeaderTooLarge,
    /// The header is smaller than 8 bytes
    HeaderTooSmall,
    /// The header length is invalid
    InvalidHeaderLength,
    /// The tensor name was not found in the archive
    TensorNotFound(String),
    /// Invalid information between shape, dtype and the proposed offsets in the file
    TensorInvalidInfo,
    /// The offsets declared for tensor with name `String` in the header are invalid
    InvalidOffset(String),
    /// IoError
    #[cfg(feature = "std")]
    IoError(std::io::Error),
    /// bincode encoder error
    EncodeError(bincode::error::EncodeError),
    /// bincode decoder error
    DecoderError(bincode::error::DecodeError),
    /// The follow tensor cannot be created because the buffer size doesn't match shape + dtype
    InvalidTensorView(Dtype, Vec<usize>, usize),
    /// The metadata is invalid because the data offsets of the tensor does not
    /// fully cover the buffer part of the file. The last offset **must** be
    /// the end of the file.
    MetadataIncompleteBuffer,
    /// The metadata contains information (shape or shape * dtype size) which lead to an
    /// arithmetic overflow. This is most likely an error in the file.
    ValidationOverflow,
    /// The metadata contains a mismatch between the index map and tensor info,  
    /// leading to unnecessary memory allocation. This is likely due to file tampering.
    ValidationMismatch,
}

#[cfg(feature = "std")]
impl From<std::io::Error> for BinTensorError {
    fn from(error: std::io::Error) -> BinTensorError {
        BinTensorError::IoError(error)
    }
}

impl From<bincode::error::DecodeError> for BinTensorError {
    fn from(error: bincode::error::DecodeError) -> BinTensorError {
        BinTensorError::DecoderError(error)
    }
}

impl From<bincode::error::EncodeError> for BinTensorError {
    fn from(error: bincode::error::EncodeError) -> BinTensorError {
        BinTensorError::EncodeError(error)
    }
}

impl core::fmt::Display for BinTensorError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        write!(f, "{self:?}")
    }
}

#[cfg(not(feature = "std"))]
impl core::error::Error for BinTensorError {}

#[cfg(feature = "std")]
impl std::error::Error for BinTensorError {}

struct PreparedData {
    n: u64,
    header_bytes: Vec<u8>,
    offset: usize,
}

/// The trait necessary to enable bintensors to serialize a tensor
/// If you have an owned tensor like this:
///
/// ```rust
/// use bintensors::tensor::{View, Dtype};
/// use std::borrow::Cow;
/// struct Tensor{ dtype: MyDtype, shape: Vec<usize>, data: Vec<u8>}
///
/// # type MyDtype = Dtype;
/// impl<'data> View for &'data Tensor{
///    fn dtype(&self) -> Dtype{
///        self.dtype.into()
///    }
///    fn shape(&self) -> &[usize]{
///         &self.shape
///    }
///    fn data(&self) -> Cow<[u8]>{
///        (&self.data).into()
///    }
///    fn data_len(&self) -> usize{
///        self.data.len()
///    }
/// }
/// ```
///
/// For a borrowed tensor:
///
/// ```rust
/// use bintensors::tensor::{View, Dtype};
/// use std::borrow::Cow;
/// struct Tensor<'data>{ dtype: MyDtype, shape: Vec<usize>, data: &'data[u8]}
///
/// # type MyDtype = Dtype;
/// impl<'data> View for Tensor<'data>{
///    fn dtype(&self) -> Dtype{
///        self.dtype.into()
///    }
///    fn shape(&self) -> &[usize]{
///         &self.shape
///    }
///    fn data(&self) -> Cow<[u8]>{
///        self.data.into()
///    }
///    fn data_len(&self) -> usize{
///        self.data.len()
///    }
/// }
/// ```
///
/// Now if you have some unknown buffer that could be on GPU for instance,
/// you can implement the trait to return an owned local buffer containing the data
/// on CPU (needed to write on disk)
/// ```rust
/// use bintensors::tensor::{View, Dtype};
/// use std::borrow::Cow;
///
/// # type MyDtype = Dtype;
/// # type OpaqueGpu = Vec<u8>;
/// struct Tensor{ dtype: MyDtype, shape: Vec<usize>, data: OpaqueGpu }
///
/// impl View for Tensor{
///    fn dtype(&self) -> Dtype{
///        self.dtype.into()
///    }
///    fn shape(&self) -> &[usize]{
///         &self.shape
///    }
///    fn data(&self) -> Cow<[u8]>{
///        // This copies data from GPU to CPU.
///        let data: Vec<u8> = self.data.to_vec();
///        data.into()
///    }
///    fn data_len(&self) -> usize{
///        let n: usize = self.shape.iter().product();
///        let bytes_per_element = self.dtype.size();
///        n * bytes_per_element
///    }
/// }
/// ```
pub trait View {
    /// The `Dtype` of the tensor
    fn dtype(&self) -> Dtype;
    /// The shape of the tensor
    fn shape(&self) -> &[usize];
    /// The data of the tensor
    fn data(&self) -> Cow<[u8]>;
    /// The length of the data, in bytes.
    /// This is necessary as this might be faster to get than `data().len()`
    /// for instance for tensors residing in GPU.
    fn data_len(&self) -> usize;
}

fn prepare<S: AsRef<str> + Ord + core::fmt::Display, V: View, I: IntoIterator<Item = (S, V)>>(
    data: I,
    data_info: &Option<HashMap<String, String>>,
    // ) -> Result<(Metadata, Vec<&'hash TensorView<'data>>, usize), BinTensorError> {
) -> Result<(PreparedData, Vec<V>), BinTensorError> {
    // Make sure we're sorting by descending dtype alignment
    // Then by name
    let mut data: Vec<_> = data.into_iter().collect();
    data.sort_by(|(lname, left), (rname, right)| {
        right.dtype().cmp(&left.dtype()).then(lname.cmp(rname))
    });

    let mut tensors: Vec<V> = Vec::with_capacity(data.len());
    let mut hmetadata = Vec::with_capacity(data.len());
    let mut offset = 0;
    let data: Vec<_> = data.into_iter().collect();
    for (name, tensor) in data {
        let n = tensor.data_len();
        let tensor_info = TensorInfo {
            dtype: tensor.dtype(),
            shape: tensor.shape().to_vec(),
            data_offsets: (offset, offset + n),
        };
        offset += n;
        hmetadata.push((name.to_string(), tensor_info));
        tensors.push(tensor);
    }

    // encode the metadata into byte buffer
    let metadata: Metadata = Metadata::new(data_info.clone(), hmetadata)?;
    let mut metadata_buf = bincode::encode_to_vec(
        metadata,
        bincode::config::standard().with_limit::<{ MAX_HEADER_SIZE }>(),
    )?;
    // Force alignment to 8 bytes with padding.
    let extra = (8 - metadata_buf.len() % 8) % 8;
    let padding = vec![b' '; extra];
    metadata_buf.extend(padding);

    let n: u64 = metadata_buf.len() as u64;
    Ok((
        PreparedData {
            n,
            header_bytes: metadata_buf,
            offset,
        },
        tensors,
    ))
}

/// Serialize to an owned byte buffer the dictionnary of tensors.
pub fn serialize<
    S: AsRef<str> + Ord + core::fmt::Display,
    V: View,
    I: IntoIterator<Item = (S, V)>,
>(
    data: I,
    data_info: &Option<HashMap<String, String>>,
) -> Result<Vec<u8>, BinTensorError> {
    let (
        PreparedData {
            n,
            header_bytes,
            offset,
        },
        tensors,
    ) = prepare(data, data_info)?;
    let expected_size = OFFSET + header_bytes.len() + offset;
    let mut buffer: Vec<u8> = Vec::with_capacity(expected_size);
    buffer.extend(&n.to_le_bytes().to_vec());
    buffer.extend(&header_bytes);
    for tensor in tensors {
        buffer.extend(tensor.data().as_ref());
    }
    Ok(buffer)
}

/// Serialize to a regular file the dictionnary of tensors.
/// Writing directly to file reduces the need to allocate the whole amount to
/// memory.
#[cfg(feature = "std")]
pub fn serialize_to_file<
    S: AsRef<str> + Ord + core::fmt::Display,
    V: View,
    I: IntoIterator<Item = (S, V)>,
    P: AsRef<Path>,
>(
    data: I,
    data_info: &Option<HashMap<String, String>>,
    filename: P,
) -> Result<(), BinTensorError> {
    let (
        PreparedData {
            n, header_bytes, ..
        },
        tensors,
    ) = prepare(data, data_info)?;
    let mut f = std::io::BufWriter::new(std::fs::File::create(filename)?);
    f.write_all(n.to_le_bytes().as_ref())?;
    f.write_all(&header_bytes)?;
    for tensor in tensors {
        f.write_all(tensor.data().as_ref())?;
    }
    f.flush()?;
    Ok(())
}

/// A structure that holds a serialized byte buffer along with its checksum.
///
/// This is typically used to serialize data (e.g., tensors) and produce a digest
/// to ensure integrity when the buffer is transmitted or stored. The `checksum`
/// is computed from the contents of `buffer`, using a specified hashing algorithm.
///
/// Fields:
/// - `checksum`: A digest (e.g., SHA-1, SHA-256) of the serialized buffer.
/// - `buffer`: The actual serialized data.
pub struct DigestBuffer {
    /// A digest (e.g., SHA-1, SHA-256) of the serialized buffer.
    pub checksum: Vec<u8>,
    /// serialized data.
    pub buffer: Vec<u8>,
}

/// Serialize to an owned byte buffer the dictionnary of tensors,
/// with a checksum idendity
///
/// ```
/// use sha1::Sha1;
///
///
/// ```
pub fn serialize_with_checksum<
    S: AsRef<str> + Ord + core::fmt::Display,
    V: View,
    I: IntoIterator<Item = (S, V)>,
    H: Digest,
>(
    data: I,
    data_info: &Option<HashMap<String, String>>,
    mut hasher: H,
) -> Result<DigestBuffer, BinTensorError> {
    let (
        PreparedData {
            n,
            header_bytes,
            offset,
        },
        tensors,
    ) = prepare(data, data_info)?;
    let expected_size = OFFSET + header_bytes.len() + offset;
    let mut buffer: Vec<u8> = Vec::with_capacity(expected_size);

    buffer.extend(&n.to_le_bytes().to_vec());
    buffer.extend(&header_bytes);

    for tensor in tensors {
        let data = tensor.data();
        buffer.extend(data.as_ref());
    }

    hasher.update(&buffer);
    Ok(DigestBuffer {
        checksum: hasher.finalize()[..].to_vec(),
        buffer,
    })
}

/// A structure owning some metadata to lookup tensors on a shared `data`
/// byte-buffer (not owned).
pub struct BinTensors<'data> {
    metadata: Metadata,
    data: &'data [u8],
}

impl core::fmt::Debug for BinTensors<'_> {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        write!(f, "BinTensors {{ {:?} }}", self.metadata)
    }
}

impl<'data> BinTensors<'data> {
    /// Given a byte-buffer representing the whole bintensor file
    /// parses the header, and returns the size of the header + the parsed data.
    pub fn read_metadata<'in_data>(
        buffer: &'in_data [u8],
    ) -> Result<(usize, Metadata), BinTensorError>
    where
        'in_data: 'data,
    {
        let buffer_len = buffer.len();
        if buffer_len < MIN_HEADER_SIZE {
            return Err(BinTensorError::HeaderTooSmall);
        }

        let arr: [u8; 8] = [
            buffer[0], buffer[1], buffer[2], buffer[3], buffer[4], buffer[5], buffer[6], buffer[7],
        ];

        let n: usize = u64::from_le_bytes(arr)
            .try_into()
            .map_err(|_| BinTensorError::HeaderTooLarge)?;
        if n > MAX_HEADER_SIZE {
            return Err(BinTensorError::HeaderTooLarge);
        }

        let stop = n
            .checked_add(OFFSET)
            .ok_or(BinTensorError::InvalidHeaderLength)?;
        if stop > buffer_len {
            return Err(BinTensorError::InvalidHeaderLength);
        }

        let (metadata, _): (Metadata, _) = bincode::decode_from_slice(
            &buffer[OFFSET..stop],
            bincode::config::standard().with_limit::<{ MAX_HEADER_SIZE }>(),
        )?;
        let buffer_end = metadata.validate()?;
        if buffer_end + OFFSET + n != buffer_len {
            return Err(BinTensorError::MetadataIncompleteBuffer);
        }
        Ok((n, metadata))
    }
    /// Given a byte-buffer representing the whole bintensor file
    /// parses it and returns the Deserialized form (No Tensor allocation).
    ///
    /// ```
    /// use bintensors::BinTensors;
    /// use memmap2::MmapOptions;
    /// use std::fs::File;
    ///
    /// let filename = "model.bt";
    /// use std::io::Write;
    /// let serialized = b"\x18\x00\x00\x00\x00\x00\x00\x00\x00\x01\x08weight_1\x00\x02\x02\x02\x00\x04       \x00\x00\x00\x00";
    /// File::create(filename).unwrap().write(serialized).unwrap();
    /// let file = File::open(filename).unwrap();
    /// let buffer = unsafe { MmapOptions::new().map(&file).unwrap() };
    /// let tensors = BinTensors::deserialize(&buffer).unwrap();
    /// let tensor = tensors
    ///         .tensor("weight_1");
    /// ```
    pub fn deserialize<'in_data>(buffer: &'in_data [u8]) -> Result<Self, BinTensorError>
    where
        'in_data: 'data,
    {
        let (n, metadata) = BinTensors::read_metadata(buffer)?;
        let data = &buffer[n + OFFSET..];
        Ok(Self { metadata, data })
    }

    /// Returns the tensors contained within the BinTensors.
    /// The tensors returned are merely views and the data is not owned by this
    /// structure.
    pub fn tensors(&self) -> Vec<(String, TensorView<'data>)> {
        let mut tensors = Vec::with_capacity(self.metadata.index_map.len());
        for (name, &index) in &self.metadata.index_map {
            let info = &self.metadata.tensors[index];
            let tensorview = TensorView {
                dtype: info.dtype,
                shape: info.shape.clone(),
                data: &self.data[info.data_offsets.0..info.data_offsets.1],
            };
            tensors.push((name.to_string(), tensorview));
        }
        tensors
    }

    /// Returns an iterator over the tensors contained within the BinTensors.
    /// The tensors returned are merely views and the data is not owned by this
    /// structure.
    pub fn iter<'a>(&'a self) -> impl Iterator<Item = (&'a str, TensorView<'data>)> {
        self.metadata.index_map.iter().map(|(name, &idx)| {
            let info = &self.metadata.tensors[idx];
            (
                name.as_str(),
                TensorView {
                    dtype: info.dtype,
                    shape: info.shape.clone(),
                    data: &self.data[info.data_offsets.0..info.data_offsets.1],
                },
            )
        })
    }

    /// Allow the user to get a specific tensor within the BinTensors.
    /// The tensor returned is merely a view and the data is not owned by this
    /// structure.
    pub fn tensor(&self, tensor_name: &str) -> Result<TensorView<'data>, BinTensorError> {
        if let Some(index) = &self.metadata.index_map.get(tensor_name) {
            if let Some(info) = &self.metadata.tensors.get(**index) {
                Ok(TensorView {
                    dtype: info.dtype,
                    shape: info.shape.clone(),
                    data: &self.data[info.data_offsets.0..info.data_offsets.1],
                })
            } else {
                Err(BinTensorError::TensorNotFound(tensor_name.to_string()))
            }
        } else {
            Err(BinTensorError::TensorNotFound(tensor_name.to_string()))
        }
    }

    /// Return the names of the tensors within the BinTensors.
    /// These are used as keys to access to the actual tensors, that can be
    /// retrieved using the tensor method.
    pub fn names(&self) -> Vec<&'_ String> {
        self.metadata.index_map.keys().collect()
    }

    /// Returns a reference to the metadata header of the BinTensors file.
    pub fn metadata(&self) -> &'_ Metadata {
        &self.metadata
    }

    /// Return how many tensors are currently stored within the BinTensors.
    #[inline]
    pub fn len(&self) -> usize {
        self.metadata.tensors.len()
    }

    /// Indicate if the BinTensors contains or not any tensor.
    #[inline]
    pub fn is_empty(&self) -> bool {
        self.metadata.tensors.is_empty()
    }
}

/// The stuct representing the header of bintensor files which allow
/// indexing into the raw byte-buffer array and how to interpret it.
#[derive(Debug)]
#[cfg_attr(feature = "std", derive(Clone))]
pub struct Metadata {
    metadata: Option<HashMap<String, String>>,
    tensors: Vec<TensorInfo>,
    index_map: HashMap<String, usize>,
}

impl Encode for Metadata {
    fn encode<E: bincode::enc::Encoder>(
        &self,
        encoder: &mut E,
    ) -> Result<(), bincode::error::EncodeError> {
        let mut buffer = vec![None; self.tensors.len()];

        for (key, &index) in &self.index_map {
            buffer[index] = Some((key, &self.tensors[index]));
        }

        let header: Vec<(&String, &TensorInfo)> =
            buffer.into_iter().map(|item| item.unwrap()).collect();

        let metadata: Option<BTreeMap<&String, &String>> = self.metadata.as_ref().map(|map| {
            let mut entries: Vec<_> = map.iter().collect();
            entries.sort_by_key(|(k, _)| *k);
            entries.into_iter().collect::<BTreeMap<_, _>>()
        });

        bincode::Encode::encode(&(metadata, header), encoder)
    }
}

impl<Context> Decode<Context> for Metadata {
    fn decode<D: bincode::de::Decoder<Context = Context>>(
        decoder: &mut D,
    ) -> Result<Self, bincode::error::DecodeError> {
        #[cfg(feature = "std")]
        let metadata = bincode::Decode::decode(decoder)?;
        #[cfg(not(feature = "std"))]
        let metadata: Option<HashMap<String, String>> = bincode::serde::decode_from_reader(
            decoder.reader(),
            bincode::config::standard().with_limit::<{ MAX_HEADER_SIZE / 2 }>(),
        )?;

        let buffer: Vec<(String, TensorInfo)> = bincode::Decode::decode(decoder)?;

        // Reconstruct tensors vector directly from buffer
        // This ensures tensors are in the exact order they were encoded
        let mut tensors = Vec::with_capacity(buffer.len());
        let mut index_map = HashMap::with_capacity(buffer.len());

        for (i, (key, tensor_info)) in buffer.into_iter().enumerate() {
            tensors.push(tensor_info);
            index_map.insert(key, i);
        }

        Ok(Metadata {
            metadata,
            tensors,
            index_map,
        })
    }
}

impl Metadata {
    fn new(
        metadata: Option<HashMap<String, String>>,
        tensors: Vec<(String, TensorInfo)>,
    ) -> Result<Self, BinTensorError> {
        let mut index_map = HashMap::with_capacity(tensors.len());

        let tensors: Vec<_> = tensors
            .into_iter()
            .enumerate()
            .map(|(index, (k, tensor))| {
                index_map.insert(k, index);
                tensor
            })
            .collect();

        let metadata = Self {
            metadata,
            tensors,
            index_map,
        };
        metadata.validate()?;
        Ok(metadata)
    }

    fn validate(&self) -> Result<usize, BinTensorError> {
        if self.index_map.len() != self.tensors.len() {
            return Err(BinTensorError::ValidationMismatch);
        }
        let mut start = 0;
        for (i, info) in self.tensors.iter().enumerate() {
            let (s, e) = info.data_offsets;
            if s != start || e < s {
                let tensor_name = self
                    .index_map
                    .iter()
                    .find_map(|(name, &index)| if index == i { Some(&name[..]) } else { None })
                    .unwrap_or("no_tensor");
                return Err(BinTensorError::InvalidOffset(tensor_name.to_string()));
            }
            start = e;
            let nelements: usize = info
                .shape
                .iter()
                .cloned()
                .try_fold(1usize, usize::checked_mul)
                .ok_or(BinTensorError::ValidationOverflow)?;
            let nbytes = nelements
                .checked_mul(info.dtype.size())
                .ok_or(BinTensorError::ValidationOverflow)?;
            if (e - s) != nbytes {
                return Err(BinTensorError::TensorInvalidInfo);
            }
        }
        Ok(start)
    }

    /// Gives back the tensor metadata
    pub fn info(&self, name: &str) -> Option<&TensorInfo> {
        let index = self.index_map.get(name)?;
        self.tensors.get(*index)
    }

    /// Gives back the tensor metadata
    pub fn tensors(&self) -> HashMap<String, &TensorInfo> {
        self.index_map
            .iter()
            .map(|(tensor_name, index)| (tensor_name.clone(), &self.tensors[*index]))
            .collect()
    }

    /// Gives back the tensor names ordered by offset
    pub fn offset_keys(&self) -> Vec<String> {
        let mut index_vec: Vec<_> = self.index_map.iter().collect();
        index_vec.sort_by_key(|a| a.1);
        index_vec.into_iter().map(|a| a.0.clone()).collect()
    }

    /// Gives back the tensor metadata
    pub fn metadata(&self) -> &Option<HashMap<String, String>> {
        &self.metadata
    }
}

/// A view of a Tensor within the file.
/// Contains references to data within the full byte-buffer
/// And is thus a readable view of a single tensor
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct TensorView<'data> {
    dtype: Dtype,
    shape: Vec<usize>,
    data: &'data [u8],
}

impl View for &TensorView<'_> {
    fn dtype(&self) -> Dtype {
        self.dtype
    }

    fn shape(&self) -> &[usize] {
        &self.shape
    }

    fn data(&self) -> Cow<[u8]> {
        self.data.into()
    }

    fn data_len(&self) -> usize {
        self.data.len()
    }
}

impl View for TensorView<'_> {
    fn dtype(&self) -> Dtype {
        self.dtype
    }

    fn shape(&self) -> &[usize] {
        &self.shape
    }

    fn data(&self) -> Cow<[u8]> {
        self.data.into()
    }

    fn data_len(&self) -> usize {
        self.data.len()
    }
}

impl<'data> TensorView<'data> {
    /// Create new tensor view
    pub fn new(dtype: Dtype, shape: Vec<usize>, data: &'data [u8]) -> Result<Self, BinTensorError> {
        let n = data.len();
        let n_elements: usize = shape.iter().product();
        if n != n_elements * dtype.size() {
            Err(BinTensorError::InvalidTensorView(dtype, shape, n))
        } else {
            Ok(Self { dtype, shape, data })
        }
    }
    /// The current tensor dtype
    pub fn dtype(&self) -> Dtype {
        self.dtype
    }

    /// The current tensor shape
    pub fn shape(&'data self) -> &'data [usize] {
        &self.shape
    }

    /// The current tensor byte-buffer
    pub fn data(&self) -> &'data [u8] {
        self.data
    }

    /// The various pieces of the data buffer according to the asked slice
    #[cfg(feature = "slice")]
    pub fn sliced_data(
        &'data self,
        slices: &[TensorIndexer],
    ) -> Result<SliceIterator<'data>, InvalidSlice> {
        SliceIterator::new(self, slices)
    }
}

/// A single tensor information.
/// Endianness is assumed to be little endian
/// Ordering is assumed to be 'C'.
#[derive(Debug, Encode, Decode, Clone)]
pub struct TensorInfo {
    /// The type of each element of the tensor
    pub dtype: Dtype,
    /// The shape of the tensor
    pub shape: Vec<usize>,
    /// The offsets to find the data within the byte-buffer array.
    pub data_offsets: (usize, usize),
}

/// The various available dtypes. They MUST be in increasing alignment order
#[derive(Debug, Clone, Copy, PartialEq, Eq, Ord, PartialOrd, Encode, Decode)]
#[non_exhaustive]
pub enum Dtype {
    /// Boolan type
    BOOL,
    /// Unsigned byte
    U8,
    /// Signed byte
    I8,
    /// FP8 <https://arxiv.org/pdf/2209.05433.pdf>_
    #[allow(non_camel_case_types)]
    F8_E5M2,
    /// FP8 <https://arxiv.org/pdf/2209.05433.pdf>_
    #[allow(non_camel_case_types)]
    F8_E4M3,
    /// Signed integer (16-bit)
    I16,
    /// Unsigned integer (16-bit)
    U16,
    /// Half-precision floating point
    F16,
    /// Brain floating point
    BF16,
    /// Signed integer (32-bit)
    I32,
    /// Unsigned integer (32-bit)
    U32,
    /// Floating point (32-bit)
    F32,
    /// Floating point (64-bit)
    F64,
    /// Signed integer (64-bit)
    I64,
    /// Unsigned integer (64-bit)
    U64,
}

impl Dtype {
    /// Gives out the size (in bytes) of 1 element of this dtype.
    ///
    /// # Reference Table
    ///
    /// | Dtype       | Size (bytes) |
    /// |-------------|--------------|
    /// | BOOL        | 1            |
    /// | U8          | 1            |
    /// | I8          | 1            |
    /// | F8_E5M2     | 1            |
    /// | F8_E4M3     | 1            |
    /// | I16         | 2            |
    /// | U16         | 2            |
    /// | F16         | 2            |
    /// | BF16        | 2            |
    /// | I32         | 4            |
    /// | U32         | 4            |
    /// | F32         | 4            |
    /// | I64         | 8            |
    /// | U64         | 8            |
    /// | F64         | 8            |
    ///
    pub fn size(&self) -> usize {
        match self {
            Dtype::BOOL | Dtype::U8 | Dtype::I8 | Dtype::F8_E5M2 | Dtype::F8_E4M3 => 1,
            Dtype::I16 | Dtype::U16 | Dtype::F16 | Dtype::BF16 => 2,
            Dtype::I32 | Dtype::F32 | Dtype::U32 => 4,
            Dtype::I64 | Dtype::U64 | Dtype::F64 => 8,
        }
    }
}

#[cfg(test)]
mod tests {

    use super::*;

    use proptest::prelude::*;
    #[cfg(not(debug_assertions))]
    use sha1::Sha1;
    #[cfg(not(debug_assertions))]
    use sha2::Sha256;
    #[cfg(not(debug_assertions))]
    use sha3::Sha3_256;
    #[cfg(not(feature = "std"))]
    extern crate std;

    #[cfg(feature = "slice")]
    use crate::slice::IndexOp;

    const MAX_DIMENSION: usize = 8;
    const MAX_SIZE: usize = 8;
    const MAX_TENSORS: usize = 8;

    fn arbitrary_dtype() -> impl Strategy<Value = Dtype> {
        prop_oneof![
            Just(Dtype::BOOL),
            Just(Dtype::U8),
            Just(Dtype::I8),
            Just(Dtype::I16),
            Just(Dtype::U16),
            Just(Dtype::I32),
            Just(Dtype::U32),
            Just(Dtype::I64),
            Just(Dtype::U64),
            Just(Dtype::F16),
            Just(Dtype::BF16),
            Just(Dtype::F32),
            Just(Dtype::F64),
        ]
    }

    fn arbitrary_shape() -> impl Strategy<Value = Vec<usize>> {
        // We do not allow empty shapes or 0 sizes.
        (1..MAX_DIMENSION).prop_flat_map(|length| prop::collection::vec(1..MAX_SIZE, length))
    }

    fn arbitrary_metadata() -> impl Strategy<Value = Metadata> {
        // We generate at least one tensor.
        (1..MAX_TENSORS)
            .prop_flat_map(|size| {
                // Returns a strategy generating `size` data types and shapes.
                (
                    prop::collection::vec(arbitrary_dtype(), size),
                    prop::collection::vec(arbitrary_shape(), size),
                )
            })
            .prop_map(|(dtypes, shapes)| {
                // Returns a valid metadata object for a random (length, dtypes, shapes) triple.
                let mut start = 0;
                let tensors: Vec<TensorInfo> = dtypes
                    .iter()
                    .zip(shapes)
                    .map(|(dtype, shape)| {
                        // This cannot overflow because the size of
                        // the vector and elements are so small.
                        let length: usize = shape.iter().product();
                        let end = start + length * dtype.size();
                        let tensor = TensorInfo {
                            dtype: *dtype,
                            shape,
                            data_offsets: (start, end),
                        };
                        start = end;
                        tensor
                    })
                    .collect();
                let index_map = (0..tensors.len())
                    .map(|index| (format!("t.{index}"), index))
                    .collect();
                Metadata {
                    metadata: None,
                    tensors,
                    index_map,
                }
            })
    }

    /// This method returns the size of the data corresponding to the metadata. It
    /// assumes that `metadata` contains at least one tensor, and that tensors are
    /// ordered by offset in `metadata.tensors`.
    ///
    /// # Panics
    ///
    /// This method will panic if `metadata` does not contain any tensors.
    fn data_size(metadata: &Metadata) -> usize {
        metadata.tensors.last().unwrap().data_offsets.1
    }

    proptest! {
        #![proptest_config(ProptestConfig::with_cases(20))]

        #[test]
        fn test_indexing(metadata in arbitrary_metadata()) {
            let data = vec![0u8; data_size(&metadata)];
            let tensors = BinTensors { metadata, data: &data };
            for name in tensors.names() {
                assert!(tensors.tensor(name).is_ok());
            }
        }
        #[test]
        fn test_roundtrip(metadata in arbitrary_metadata()) {
            let data: Vec<u8> = (0..data_size(&metadata)).map(|x| x as u8).collect();
            let before = BinTensors { metadata, data: &data };
            let tensors = before.tensors();
            let bytes = serialize(tensors.iter().map(|(name, view)| (name.to_string(), view)), &None).unwrap();

            let after = BinTensors::deserialize(&bytes).unwrap();

            // Check that the tensors are the same after deserialization.
            assert_eq!(before.names().len(), after.names().len());
            for name in before.names() {
                let tensor_before = before.tensor(name).unwrap();
                let tensor_after = after.tensor(name).unwrap();
                assert_eq!(tensor_after.data().as_ptr() as usize % tensor_after.dtype().size(), 0);
                assert_eq!(tensor_before, tensor_after);
            }
        }
    }

    #[test]
    fn test_serialization() {
        let data: Vec<u8> = vec![0.0f32, 1.0, 2.0, 3.0, 4.0, 5.0]
            .into_iter()
            .flat_map(|f| f.to_le_bytes())
            .collect();
        let shape = vec![1, 2, 3];
        let attn_0 = TensorView::new(Dtype::F32, shape, &data).unwrap();
        let metadata: HashMap<String, TensorView> =
            [("attn.0".to_string(), attn_0)].into_iter().collect();

        let out = serialize(&metadata, &None).unwrap();
        assert_eq!(
            out,
            [
                16, 0, 0, 0, 0, 0, 0, 0, 0, 1, 6, 97, 116, 116, 110, 46, 48, 11, 3, 1, 2, 3, 0, 24,
                0, 0, 0, 0, 0, 0, 128, 63, 0, 0, 0, 64, 0, 0, 64, 64, 0, 0, 128, 64, 0, 0, 160, 64
            ]
        );
        let _ = BinTensors::deserialize(&out).unwrap();
    }

    #[test]
    fn test_empty() {
        let tensors: HashMap<String, TensorView> = HashMap::new();
        let out = serialize(&tensors, &None).unwrap();
        assert_eq!(out, [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 32, 32, 32, 32, 32]);
        let _ = BinTensors::deserialize(&out).unwrap();
    }

    #[test]
    fn test_serialization_forced_alignement() {
        let data: Vec<u8> = vec![0.0f32, 1.0, 2.0, 3.0, 4.0, 5.0]
            .into_iter()
            .flat_map(|f| f.to_le_bytes())
            .collect();
        let shape = vec![1, 1, 2, 3];
        let attn_0 = TensorView::new(Dtype::F32, shape, &data).unwrap();
        let metadata: HashMap<String, TensorView> =
                // Smaller string to force misalignment compared to previous test.
                [("attn0".to_string(), attn_0)].into_iter().collect();
        // println!("{:?} {:?}", Dtype::F32.size(), metadata);
        let out = serialize(&metadata, &None).unwrap();
        assert_eq!(
            out,
            [
                16, 0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 97, 116, 116, 110, 48, 11, 4, 1, 1, 2, 3, 0, 24,
                0, 0, 0, 0, 0, 0, 128, 63, 0, 0, 0, 64, 0, 0, 64, 64, 0, 0, 128, 64, 0, 0, 160, 64
            ],
        );
        let parsed = BinTensors::deserialize(&out).unwrap();
        let tensor = parsed.tensor("attn0").unwrap();

        assert_eq!(tensor.data().as_ptr() as usize % tensor.dtype().size(), 0);
    }

    #[cfg(feature = "slice")]
    #[test]
    fn test_slicing() {
        let data: Vec<u8> = vec![0.0f32, 1.0, 2.0, 3.0, 4.0, 5.0]
            .into_iter()
            .flat_map(|f| f.to_le_bytes())
            .collect();
        let attn_0 = TensorView {
            dtype: Dtype::F32,
            shape: vec![1, 2, 3],
            data: &data,
        };
        let metadata: HashMap<String, TensorView> =
            [("attn.0".to_string(), attn_0)].into_iter().collect();

        let out = serialize(&metadata, &None).unwrap();
        let parsed = BinTensors::deserialize(&out).unwrap();

        let out_buffer: Vec<u8> = parsed
            .tensor("attn.0")
            .unwrap()
            .slice((.., ..1))
            .unwrap()
            .flat_map(|b| b.to_vec())
            .collect();
        assert_eq!(out_buffer, vec![0u8, 0, 0, 0, 0, 0, 128, 63, 0, 0, 0, 64]);
        assert_eq!(
            out_buffer,
            vec![0.0f32, 1.0, 2.0]
                .into_iter()
                .flat_map(|f| f.to_le_bytes())
                .collect::<Vec<_>>()
        );
        let out_buffer: Vec<u8> = parsed
            .tensor("attn.0")
            .unwrap()
            .slice((.., .., ..1))
            .unwrap()
            .flat_map(|b| b.to_vec())
            .collect();
        assert_eq!(out_buffer, vec![0u8, 0, 0, 0, 0, 0, 64, 64]);
        assert_eq!(
            out_buffer,
            vec![0.0f32, 3.0]
                .into_iter()
                .flat_map(|f| f.to_le_bytes())
                .collect::<Vec<_>>()
        );
    }

    #[test]
    fn test_gpt2() {
        gpt2_like(12, "gpt2");
    }

    #[test]
    fn test_gpt2_tiny() {
        gpt2_like(6, "gpt2_tiny");
    }

    fn gpt2_like(n_heads: usize, model_id: &str) {
        let mut tensors_desc = vec![];
        tensors_desc.push(("wte".to_string(), vec![50257, 768]));
        tensors_desc.push(("wpe".to_string(), vec![1024, 768]));
        for i in 0..n_heads {
            tensors_desc.push((format!("h.{i}.ln_1.weight"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_1.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.attn.bias"), vec![1, 1, 1024, 1024]));
            tensors_desc.push((format!("h.{i}.attn.c_attn.weight"), vec![768, 2304]));
            tensors_desc.push((format!("h.{i}.attn.c_attn.bias"), vec![2304]));
            tensors_desc.push((format!("h.{i}.attn.c_proj.weight"), vec![768, 768]));
            tensors_desc.push((format!("h.{i}.attn.c_proj.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_2.weight"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_2.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.mlp.c_fc.weight"), vec![768, 3072]));
            tensors_desc.push((format!("h.{i}.mlp.c_fc.bias"), vec![3072]));
            tensors_desc.push((format!("h.{i}.mlp.c_proj.weight"), vec![3072, 768]));
            tensors_desc.push((format!("h.{i}.mlp.c_proj.bias"), vec![768]));
        }
        tensors_desc.push(("ln_f.weight".to_string(), vec![768]));
        tensors_desc.push(("ln_f.bias".to_string(), vec![768]));

        let dtype = Dtype::F32;
        let n: usize = tensors_desc
            .iter()
            .map(|(_, shape)| shape.iter().product::<usize>())
            .sum::<usize>()
            * dtype.size(); // 4
        let all_data = vec![0; n];
        let mut metadata = HashMap::with_capacity(tensors_desc.len());
        let mut offset = 0;
        for (name, shape) in tensors_desc {
            let n: usize = shape.iter().product();
            let buffer = &all_data[offset..offset + n * dtype.size()];
            let tensor = TensorView::new(dtype, shape, buffer).unwrap();
            metadata.insert(name, tensor);
            offset += n;
        }

        let filename = format!("./out_{model_id}.bintensors");

        let out = serialize(&metadata, &None).unwrap();
        std::fs::write(&filename, out).unwrap();
        let raw = std::fs::read(&filename).unwrap();
        let _deserialized = BinTensors::deserialize(&raw).unwrap();
        std::fs::remove_file(&filename).unwrap();

        // File api
        #[cfg(feature = "std")]
        {
            serialize_to_file(&metadata, &None, std::path::Path::new(&filename)).unwrap();
            let raw = std::fs::read(&filename).unwrap();
            let _deserialized = BinTensors::deserialize(&raw).unwrap();
            std::fs::remove_file(&filename).unwrap();
        }
    }

    #[test]
    fn test_deserialization() {
        let serialized = b"\x10\x00\x00\x00\x00\x00\x00\x00\x00\x01\x04test\x00\x02\x02\x02\x00\x04   \x00\x00\x00\x00";
        let loaded = BinTensors::deserialize(serialized).unwrap();
        assert_eq!(loaded.names(), vec!["test"]);
        let tensor = loaded.tensor("test").unwrap();
        assert!(!tensor.shape().is_empty());
        assert_eq!(tensor.dtype(), Dtype::BOOL);
        // 4 bytes
        assert_eq!(tensor.data(), b"\0\0\0\0");
    }

    #[test]
    fn test_lifetimes() {
        let serialized = b"\x10\x00\x00\x00\x00\x00\x00\x00\x00\x01\x04test\x00\x02\x02\x02\x00\x04   \x00\x00\x00\x00";

        let decoded = BinTensors::deserialize(serialized).unwrap();
        let tensor = decoded.tensor("test").unwrap();

        assert_eq!(tensor.shape(), vec![2, 2]);
        assert_eq!(tensor.dtype(), Dtype::BOOL);
        // 4 bytes
        assert_eq!(tensor.data(), b"\0\0\0\0");
    }

    #[cfg(feature = "std")]
    #[test]
    fn test_offset_attack() {
        let mut tensors = Vec::new();
        let mut index_map = HashMap::new();
        let dtype = Dtype::F32;
        let shape = vec![2, 2];
        let data_offsets = (0, 16);
        for i in 0..10 {
            let key = format!("weight_{i}");
            tensors.push(TensorInfo {
                dtype,
                shape: shape.clone(),
                data_offsets,
            });
            index_map.insert(key, i);
        }

        let metadata = Metadata {
            metadata: None,
            tensors,
            index_map,
        };

        let serialized = bincode::encode_to_vec(metadata, bincode::config::standard()).unwrap();
        let n = serialized.len();

        let filename = "out.bintensors";
        let mut f = std::io::BufWriter::new(std::fs::File::create(filename).unwrap());
        f.write_all(n.to_le_bytes().as_ref()).unwrap();
        f.write_all(&serialized).unwrap();
        f.write_all(b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0").unwrap();
        f.flush().unwrap();

        let reloaded = std::fs::read(filename).unwrap();
        match BinTensors::deserialize(&reloaded) {
            Err(BinTensorError::InvalidOffset(_)) => {
                // Yes we have the correct error
                std::fs::remove_file(filename).unwrap();
            }
            Err(err) => panic!("Unexpected error {err:?}"),
            Ok(_) => panic!("This should not be able to be deserialized"),
        }
    }

    #[test]
    fn test_metadata_incomplete_buffer() {
        let serialized = b"\x10\x00\x00\x00\x00\x00\x00\x00\x00\x01\x09\x02\x01\x04\x00\x10\x01\x04\x74\x65\x73\x74\x00\x20\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0hello_world";

        match BinTensors::deserialize(serialized) {
            Err(BinTensorError::MetadataIncompleteBuffer) => {
                // Yes we have the correct error
            }
            Err(BinTensorError::DecoderError(_)) => {
                // Yes we have the correct error
            }
            _ => panic!("This should not be able to be deserialized"),
        }

        // Missing data in the buffer
        let serialized = b"\x10\x00\x00\x00\x00\x00\x00\x00\x01\x09\x02\x04\x74\x65\x73\x00\x20\0\0\0\0\0\0\0\0\0\0\0\0\0\0"; // <--- missing 2 bytes

        match BinTensors::deserialize(serialized) {
            Err(BinTensorError::MetadataIncompleteBuffer) => {
                // Yes we have the correct error
            }
            Err(BinTensorError::DecoderError(_)) => {
                // Yes we have the correct error
            }
            _ => panic!("This should not be able to be deserialized"),
        }
    }

    #[test]
    fn test_header_too_large() {
        let serialized = b"\x10\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x01\x09\x02\x01\x04\x00\x10\x01\x04\x74\x65\x73\x74\x00\x20\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0";

        match BinTensors::deserialize(serialized) {
            Err(BinTensorError::HeaderTooLarge) => {
                // Yes we have the correct error
            }
            _ => panic!("This should not be able to be deserialized"),
        }
    }

    #[test]
    fn test_header_too_small() {
        let serialized = b"";
        match BinTensors::deserialize(serialized) {
            Err(BinTensorError::HeaderTooSmall) => {
                // Yes we have the correct error
            }
            _ => panic!("This should not be able to be deserialized"),
        }
    }

    #[test]
    fn test_invalid_header_length() {
        let serialized = b"<\x00\x00\x00\x00\x00\x00\x00";
        match BinTensors::deserialize(serialized) {
            Err(BinTensorError::InvalidHeaderLength) => {
                // Yes we have the correct error
            }
            _ => panic!("This should not be able to be deserialized"),
        }
    }

    #[test]
    fn test_invalid_header_non_valid() {
        let serialized = b"\x01\x00\x00\x00\x00\x00\x00\x00\xff";
        match BinTensors::deserialize(serialized) {
            Err(BinTensorError::DecoderError(_)) => {
                // Yes we have the correct error
            }
            _ => panic!("This should not be able to be deserialized"),
        }
    }

    #[cfg(not(debug_assertions))]
    /// This should only return one Vec<u8>
    fn dummy_data_checksum() -> Vec<u8> {
        let mut tensors_desc: Vec<(String, Vec<usize>)> = Vec::new();

        tensors_desc.push(("ln_f.weight".to_string(), vec![768, 768]));
        tensors_desc.push(("ln_f.bias".to_string(), vec![768]));

        let dtype = Dtype::F32;
        let n: usize = tensors_desc
            .iter()
            .map(|(_, shape)| shape.iter().product::<usize>())
            .sum::<usize>()
            * dtype.size(); // 4
        let all_data = vec![0; n];
        let mut metadata = HashMap::with_capacity(tensors_desc.len());
        let mut offset = 0;
        for (name, shape) in tensors_desc {
            let n: usize = shape.iter().product();
            let buffer = &all_data[offset..offset + n * dtype.size()];
            let tensor = TensorView::new(dtype, shape, buffer).unwrap();
            metadata.insert(name, tensor);
            offset += n;
        }

        let mut hasher = Sha1::new();
        let b = serialize(metadata, &None).unwrap();
        hasher.update(&b);

        hasher.finalize()[..].to_vec()
    }

    #[cfg(not(debug_assertions))]
    #[test]
    fn test_metadata_buffer() {
        assert_eq!(dummy_data_checksum(), dummy_data_checksum())
    }

    /// Only run these on release because they are really slow
    #[cfg(not(debug_assertions))]
    #[test]
    fn test_checksum_sha1() {
        let n_heads = 5;
        let mut tensors_desc = vec![];
        tensors_desc.push(("wte".to_string(), vec![50257, 768]));
        tensors_desc.push(("wpe".to_string(), vec![1024, 768]));
        for i in 0..n_heads {
            tensors_desc.push((format!("h.{i}.ln_1.weight"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_1.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.attn.bias"), vec![1, 1, 1024, 1024]));
            tensors_desc.push((format!("h.{i}.attn.c_attn.weight"), vec![768, 2304]));
            tensors_desc.push((format!("h.{i}.attn.c_attn.bias"), vec![2304]));
            tensors_desc.push((format!("h.{i}.attn.c_proj.weight"), vec![768, 768]));
            tensors_desc.push((format!("h.{i}.attn.c_proj.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_2.weight"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_2.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.mlp.c_fc.weight"), vec![768, 3072]));
            tensors_desc.push((format!("h.{i}.mlp.c_fc.bias"), vec![3072]));
            tensors_desc.push((format!("h.{i}.mlp.c_proj.weight"), vec![3072, 768]));
            tensors_desc.push((format!("h.{i}.mlp.c_proj.bias"), vec![768]));
        }
        tensors_desc.push(("ln_f.weight".to_string(), vec![768]));
        tensors_desc.push(("ln_f.bias".to_string(), vec![768]));

        let dtype = Dtype::F32;
        let n: usize = tensors_desc
            .iter()
            .map(|(_, shape)| shape.iter().product::<usize>())
            .sum::<usize>()
            * dtype.size(); // 4
        let all_data = vec![0; n]; // Make `all_data` a `Vec<u8>`
        let mut metadata: HashMap<String, TensorView<'_>> =
            HashMap::with_capacity(tensors_desc.len());
        let mut offset = 0;

        // Adjust this loop to use owned data properly
        for (name, shape) in tensors_desc {
            let n: usize = shape.iter().product();
            let buffer = &all_data[offset..offset + n * dtype.size()];
            let tensor = TensorView::new(dtype, shape, buffer).unwrap();
            metadata.insert(name, tensor);
            offset += n;
        }

        let hasher = Sha1::new();
        let DigestBuffer { checksum, .. } =
            serialize_with_checksum(metadata, &None, hasher).unwrap();
        assert_eq!(
            checksum,
            &[
                47, 102, 227, 29, 151, 101, 28, 132, 166, 233, 33, 96, 254, 247, 131, 82, 69, 129,
                67, 237
            ]
        )
    }

    /// Only run these on release because they are really slow
    #[cfg(not(debug_assertions))]
    #[test]
    fn test_check_sha2() {
        let n_heads = 5;
        let mut tensors_desc = vec![];
        tensors_desc.push(("wte".to_string(), vec![50257, 768]));
        tensors_desc.push(("wpe".to_string(), vec![1024, 768]));
        for i in 0..n_heads {
            tensors_desc.push((format!("h.{i}.ln_1.weight"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_1.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.attn.bias"), vec![1, 1, 1024, 1024]));
            tensors_desc.push((format!("h.{i}.attn.c_attn.weight"), vec![768, 2304]));
            tensors_desc.push((format!("h.{i}.attn.c_attn.bias"), vec![2304]));
            tensors_desc.push((format!("h.{i}.attn.c_proj.weight"), vec![768, 768]));
            tensors_desc.push((format!("h.{i}.attn.c_proj.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_2.weight"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_2.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.mlp.c_fc.weight"), vec![768, 3072]));
            tensors_desc.push((format!("h.{i}.mlp.c_fc.bias"), vec![3072]));
            tensors_desc.push((format!("h.{i}.mlp.c_proj.weight"), vec![3072, 768]));
            tensors_desc.push((format!("h.{i}.mlp.c_proj.bias"), vec![768]));
        }
        tensors_desc.push(("ln_f.weight".to_string(), vec![768]));
        tensors_desc.push(("ln_f.bias".to_string(), vec![768]));

        let dtype = Dtype::F32;
        let n: usize = tensors_desc
            .iter()
            .map(|(_, shape)| shape.iter().product::<usize>())
            .sum::<usize>()
            * dtype.size(); // 4
        let all_data = vec![0; n]; // Make `all_data` a `Vec<u8>`
        let mut metadata: HashMap<String, TensorView<'_>> =
            HashMap::with_capacity(tensors_desc.len());
        let mut offset = 0;

        // Adjust this loop to use owned data properly
        for (name, shape) in tensors_desc {
            let n: usize = shape.iter().product();
            let buffer = &all_data[offset..offset + n * dtype.size()];
            let tensor = TensorView::new(dtype, shape, buffer).unwrap();
            metadata.insert(name, tensor);
            offset += n;
        }

        let hasher = Sha256::new();
        let DigestBuffer { checksum, .. } =
            serialize_with_checksum(metadata, &None, hasher).unwrap();
        assert_eq!(
            checksum,
            &[
                123, 75, 249, 49, 72, 79, 229, 209, 172, 40, 79, 47, 31, 205, 108, 5, 149, 67, 105,
                217, 99, 137, 162, 119, 235, 118, 113, 44, 69, 26, 163, 211
            ]
        )
    }

    /// Only run these on release because they are really slow
    #[cfg(not(debug_assertions))]
    #[test]
    fn test_check_sha3() {
        let n_heads = 5;
        let mut tensors_desc = vec![];
        tensors_desc.push(("wte".to_string(), vec![50257, 768]));
        tensors_desc.push(("wpe".to_string(), vec![1024, 768]));
        for i in 0..n_heads {
            tensors_desc.push((format!("h.{i}.ln_1.weight"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_1.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.attn.bias"), vec![1, 1, 1024, 1024]));
            tensors_desc.push((format!("h.{i}.attn.c_attn.weight"), vec![768, 2304]));
            tensors_desc.push((format!("h.{i}.attn.c_attn.bias"), vec![2304]));
            tensors_desc.push((format!("h.{i}.attn.c_proj.weight"), vec![768, 768]));
            tensors_desc.push((format!("h.{i}.attn.c_proj.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_2.weight"), vec![768]));
            tensors_desc.push((format!("h.{i}.ln_2.bias"), vec![768]));
            tensors_desc.push((format!("h.{i}.mlp.c_fc.weight"), vec![768, 3072]));
            tensors_desc.push((format!("h.{i}.mlp.c_fc.bias"), vec![3072]));
            tensors_desc.push((format!("h.{i}.mlp.c_proj.weight"), vec![3072, 768]));
            tensors_desc.push((format!("h.{i}.mlp.c_proj.bias"), vec![768]));
        }
        tensors_desc.push(("ln_f.weight".to_string(), vec![768]));
        tensors_desc.push(("ln_f.bias".to_string(), vec![768]));

        let dtype = Dtype::F32;
        let n: usize = tensors_desc
            .iter()
            .map(|(_, shape)| shape.iter().product::<usize>())
            .sum::<usize>()
            * dtype.size(); // 4
        let all_data = vec![0; n]; // Make `all_data` a `Vec<u8>`
        let mut metadata: HashMap<String, TensorView<'_>> =
            HashMap::with_capacity(tensors_desc.len());
        let mut offset = 0;

        // Adjust this loop to use owned data properly
        for (name, shape) in tensors_desc {
            let n: usize = shape.iter().product();
            let buffer = &all_data[offset..offset + n * dtype.size()];
            let tensor = TensorView::new(dtype, shape, buffer).unwrap();
            metadata.insert(name, tensor);
            offset += n;
        }

        let hasher = Sha3_256::new();
        let DigestBuffer { checksum, .. } =
            serialize_with_checksum(metadata, &None, hasher).unwrap();
        assert_eq!(
            checksum,
            &[
                49, 8, 133, 128, 137, 157, 0, 20, 99, 208, 176, 9, 60, 147, 117, 232, 12, 239, 55,
                90, 103, 195, 21, 235, 62, 6, 242, 39, 129, 122, 89, 21
            ]
        )
    }

    #[test]
    fn test_out() {
        let mut v1: Vec<u8> = vec![0, 1, 2, 3];
        let v2: Vec<u8> = vec![5, 6, 7, 8];

        v1.iter_mut().zip(v2.iter()).for_each(|(x1, x2)| *x1 ^= *x2);

        println!("{:?}", v1.iter().sum::<u8>());

        for v in v1 {
            println!("{:#04b}", v);
        }
    }
}
